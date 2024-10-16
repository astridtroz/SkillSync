# myapp/views.py

from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Event, MemberNomination
from .serializers import NominateMemberSerializer
from dashboard.models import CustomUser
import logging
from django.http import JsonResponse
from django.views import View
import json

logger = logging.getLogger(__name__)

def get_members(request):
    # Ensure that the user is logged in
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)
    
    # Get the project associated with the request.user
    user_project = request.user.project
    members = CustomUser.objects.filter(project=user_project, user_type='member')
    members_list = list(members.values('id', 'username', 'email'))
    return JsonResponse(members_list, safe=False)

def calendar_view(request):
    context = {
        'user_role': request.user.user_type,
    }
    return render(request, 'events/calendar.html', context)

def get_events(request):
    events = Event.objects.all().values('id', 'title', 'start', 'end', 'description', 'organizer_id')
    events_list = list(events)
    return JsonResponse(events_list, safe=False)

@csrf_exempt
@require_POST
def create_event(request):
    title = request.POST.get('title')
    description = request.POST.get('description')
    start = request.POST.get('start')
    end = request.POST.get('end')
    organizer = request.user

    if not (title and description and start and end):
        return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)

    event = Event.objects.create(
        title=title,
        description=description,
        start=start,
        end=end,
        organizer=organizer
    )
    
    leaders = CustomUser.objects.filter(user_type='leader')
    leader_emails = [leader.email for leader in leaders]
    
    try:
        send_mail(
            subject='New Event Created',
            message=f'An event titled "{title}" has been created by {request.user.username}.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=leader_emails,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending mail: {e}")
    
    return JsonResponse({'status': 'success', 'event': {
        'id': event.id,
        'title': event.title,
        'start': event.start,
        'end': event.end,
        'description': event.description
    }})

@csrf_exempt
@require_POST
def delete_event(request):
    event_id = request.POST.get('id')

    event = get_object_or_404(Event, id=event_id)

    if event.organizer == request.user:
        event.delete()
        return JsonResponse({'status': 'success'})
    else:
        return HttpResponseForbidden("You are not allowed to delete this event.")

@csrf_exempt
@require_POST
def check_event_permission(request):
    event_id = request.POST.get('id')
    event = get_object_or_404(Event, id=event_id)
    can_delete = event.organizer == request.user
    return JsonResponse({'can_delete': can_delete})



class NominateMemberView(View):
    @csrf_exempt
    def post(self, request, event_id):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=403)
        
        try:
            data = json.loads(request.body)
            members = data.get('members', [])
            print(members)
            if not members:
                return JsonResponse({'status': 'error', 'message': 'No members selected'}, status=400)
            #event = Event.objects.get(id=event_id)
            if event_id:
                print(event_id)
            else:
                print("no event id recieved")
            
            real_members= CustomUser.objects.filter(id__in = members)
            member_names = ', '.join([member.username for member in real_members])
            print(member_names)            
            event = Event.objects.get(id=event_id)
            print(event.title)
            organizer=event.organizer
            print(organizer)
            print(organizer.email)
            subject=f'Members Nominated for Event by { request.user}' 
            message = f'The following members have been nominated for the event  {member_names}.'
            from_email= settings.DEFAULT_FROM_EMAIL
            recipient_list = [organizer.email]
            try:
                send_mail(subject=subject,
                        message= message,
                        from_email= from_email,
                        recipient_list=recipient_list,
                        fail_silently=False,)
            except Exception as e:
                logger.error(f"Error sending mail: {e}")

            return JsonResponse({'status': 'success'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_POST
def handle_nomination(request):
    if request.method == 'POST':
        nomination_id = request.POST.get('nomination_id')
        action = request.POST.get('action') 
        reason = request.POST.get('reason', '')

        nomination = get_object_or_404(MemberNomination, id=nomination_id, event__organizer=request.user)

        if action == 'approve':
            nomination.status = 'approved'
            nomination.save()
            
            member_email = nomination.member.email
            zoom_link = "https://zoom.us/j/123456789"  # Replace with actual Zoom link
            try:
                send_mail(
                    subject='You Have Been Approved for an Event',
                    message=f'You have been approved to attend the event "{nomination.event.title}". Join using the following link: {zoom_link}.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[member_email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Error sending mail: {e}")
                
        elif action == 'reject':
            nomination.status = 'rejected'
            nomination.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

def get_nominations(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    nominations = MemberNomination.objects.filter(event=event).values('id', 'member__username', 'status', 'reason')
    return JsonResponse(list(nominations), safe=False)
