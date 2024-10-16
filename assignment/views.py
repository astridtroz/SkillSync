import requests
from django.http import Http404, JsonResponse, HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Assignment, Video, Progress, Notification
from .forms import CreateAssignmentForm, ProgressForm
from dashboard.models import *
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, Image
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
 
def save_video(video_id, title, youtube_url, duration):
    video, created = Video.objects.get_or_create(
        youtube_id=video_id,
        defaults={'title': title, 'youtube_url': youtube_url, 'duration': duration}
    )
    if created:
        print(f"Video with ID {video_id} created.")
    else:
        print(f"Video with ID {video_id} already exists.")


def get_video_duration(video_id):
    api_key = 'AIzaSyCrEnKkYXJrJApB3EjXBj9NadAVp_Oc6PQ'
    url = f"https://www.googleapis.com/youtube/v3/videos"
    params = {
        'part': 'contentDetails',
        'id': video_id,
        'key': api_key
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    items = data.get('items', [])
    if items:
        duration = items[0]['contentDetails']['duration']
        # Convert ISO 8601 duration format to seconds
        return parse_duration(duration)
    return 0

def parse_duration(duration):
    import isodate
    duration = isodate.parse_duration(duration)
    return int(duration.total_seconds())

def search_videos(query, max_results=10):
    api_key = 'AIzaSyCrEnKkYXJrJApB3EjXBj9NadAVp_Oc6PQ'
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'key': api_key
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    videos = []
    for item in data.get('items', []):
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        youtube_url = f'https://www.youtube.com/watch?v={video_id}'
        duration = get_video_duration(video_id)
        
        # Check if video already exists
        video, created = Video.objects.get_or_create(
            youtube_id=video_id,
            defaults={'title': title, 'youtube_url': youtube_url, 'duration': duration}
        )
        if created:
            print(f"Video with ID {video_id} created.")
        else:
            print(f"Video with ID {video_id} already exists.")
        
        videos.append({'id': video_id, 'title': title, 'youtube_url': youtube_url, 'duration': duration})
    
    return videos


@login_required
def search_videos_view(request):
    query = request.GET.get('q', '')
    videos = []
    if query:
        videos = search_videos(query)

    if request.method == 'POST':
        selected_videos = request.POST.getlist('videos')
        if selected_videos:
            request.session['selected_videos'] = selected_videos
            return redirect('create_assignment')

    return render(request, 'assignment/search_videos.html', {'videos': videos})

def create_assignment(request):
    selected_video_ids = request.session.get('selected_videos', [])
    print(f"Selected video IDs: {selected_video_ids}")  # Debugging line
    
    if request.method == 'POST':
        form = CreateAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            
            # Attach selected videos to the assignment
            for video_id in selected_video_ids:
                try:
                    video = get_object_or_404(Video, youtube_id=video_id)
                    assignment.videos.add(video)
                except Http404:
                    print(f"Video with ID {video_id} not found.")
            
            form.save_m2m()  # Save many-to-many fields
            request.session.pop('selected_videos', None)
            notify_user(assignment.assigned_to, f"You have been assigned a new assignment: {assignment.title}")
            if request.user.is_leader():
                return redirect('leader_profile')
            else:
                return redirect('view_assignments')
        else:
            print("Form is not valid:", form.errors)
    else:
        form = CreateAssignmentForm()

    return render(request, 'assignment/search_videos.html', {'form': form})




@login_required
def view_assignments(request):
    assignments = Assignment.objects.filter( assigned_to =request.user)
    return render(request, 'assignment/view_assignments.html', {'assignments': assignments})

@login_required
def view_progress(request, assignment_id):
    print(f"Request user: {request.user}")  # Debug: Print current user
    print(f"Requested assignment ID: {assignment_id}")  # Debug: Print requested assignment ID
    
    assignment = get_object_or_404(Assignment, id=assignment_id, assigned_to=request.user)
    
    if request.method == 'POST':
        if 'completed' in request.POST:
            assignment.completed = True
            assignment.save()
            progresses = Progress.objects.filter(assignment=assignment, member=request.user)
            for progress in progresses:
                progress.completed = True
                progress.save()

            # Notify user
            notify_user(request.user, assignment)
            notify_user(assignment.created_by, assignment)
            
            return JsonResponse({'status': 'completed'})
    else:
        videos = assignment.videos.all()
        return render(request, 'assignment/view_progress.html', {'assignment': assignment, 'videos': videos, 'comp': assignment.completed})



def notify_user(user, assignment):
    pdf = generate_certificate(user, assignment)
    if pdf:
        subject = 'Completion Certificate'
        message = f'Dear {user.username},\n\nPlease find attached your certificate of completion for the assignment {assignment.title}.'
        from_email = 'no-reply@example.com'
        to_email = user.email
        email = EmailMessage(subject, message, from_email, [to_email])
        email.attach(f'certificate_{user.username}.pdf', pdf, 'application/pdf')
        try:
            email.send()
            print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Error sending email: {e}")
    else:
        print(f"Failed to generate PDF for user {user.username}. No email sent.")





def generate_certificate(user, assignment):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    
    elements = []
    
    # Title
    title_style = styles['Title']
    title_style.fontSize = 36
    title = Paragraph("Certificate of Completion", title_style)
    
    # Spacer
    elements.append(title)
    elements.append(Spacer(1, 0.5 * inch))

    
    # Description
    body_style = styles['BodyText']
    body_style.fontSize = 18
    description = Paragraph(
        f"This is to certify that {user.username} has successfully completed the "
        f"assignment <strong>{assignment.title}</strong> on {timezone.now().date():%B %d, %Y}.",
        
    )
    
    elements.append(description)
    elements.append(Spacer(1, 0.5 * inch))
    
    # Footer (Optional)
    footer_style = styles['Normal']
    footer_style.fontSize = 14
    footer = Paragraph("Presented by HCLtech", footer_style)
    
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

