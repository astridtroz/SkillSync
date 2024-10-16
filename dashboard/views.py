from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.viewsets import ModelViewSet
from django.contrib import messages
from .models import CustomUser, Skill
from .forms import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse
import requests
from assignment.models import *

# Create your views here.


def welcome(request):
    return render(request, 'index.html')


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm

def register(request):
    if request.method=='POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
            user=form.save()
            username = form.cleaned_data['username']         
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1==password2:
              user.set_password(password1)
              user.save()
              messages.success(request, f'Your Account has been created {username} ! Proceed to log in')
              return redirect('login')
            else:
                form.add_error('Passwords entered do not match')
    else:
        form=RegistrationForm()
    return render(request, 'dashboard/register.html',{'form':form})

def login_view(request):
    if request.method=='POST':
        print("entered")
        try:
           form=LoginForm(request.POST)
        except:
            print("cant create form")
 
        if form.is_valid():
            print("valid form")
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            user=authenticate(request, username=username, password=password)
            if user :
                login(request , user)
                if user.is_member():
                         
                   return redirect(reverse('member_profile', kwargs={'id': user.id}))
                elif user.is_leader():
                    return redirect('leader_profile')
            
        
    else:
        form=LoginForm()
    return render(request, 'dashboard/login.html', {'form':form})

@login_required
def home_view(request):
    return render(request, 'dashboard/home.html')

def user_logout(request):
    logout(request)
    return redirect('login')


class ManageSkillsView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if not isinstance(user, CustomUser):
            return redirect('login')

        search_query = request.GET.get('search', '')
        all_skills = Skill.objects.all()

        if search_query:
            available_skills = all_skills.filter(name__icontains=search_query)
        else:
            available_skills = all_skills[:4]

        user_skills = user.skills.all()

        form = SkillAddForm()

        return render(request, 'manage_skills.html', {
            'available_skills': available_skills,
            'user_skills': user_skills,
            'form': form,
            'search_query': search_query
        })

    def post(self, request, *args, **kwargs):
        user = request.user
        if not isinstance(user, CustomUser):
            return redirect('login')

        if 'add_skill' in request.POST:
            form = SkillAddForm(request.POST)
            if form.is_valid():
                new_skill_name = form.cleaned_data['name']
                competency = form.cleaned_data['competency']
                skill, created = Skill.objects.get_or_create(name=new_skill_name, defaults={'competency': competency})

                if created:
                    messages.success(request, f'New skill "{new_skill_name}" added with competency "{competency}".')
                else:
                    skill.competency = competency
                    skill.save()
                    messages.info(request, f'Skill "{new_skill_name}" already exists. Competency updated to "{competency}".')

                user.skills.add(skill)
                user.save()

        if 'update_skills' in request.POST:
            selected_skill_ids = request.POST.getlist('skills')
            selected_skills = Skill.objects.filter(id__in=selected_skill_ids)
            for skill in selected_skills:
                competency = request.POST.get(f'competency_{skill.id}', skill.competency)
                skill.competency = competency
                skill.save()
                user.skills.add(skill)
            user.save()
            messages.success(request, 'Skills and competencies updated successfully.')

        if 'delete_skill' in request.POST:
            skill_id = request.POST.get('delete_skill')
            skill_to_delete = Skill.objects.get(id=skill_id)
            user.skills.remove(skill_to_delete)
            user.save()
            messages.success(request, f'Skill "{skill_to_delete.name}" removed successfully.')

        return redirect('manage_skills')


class MemberProfileView(View):
    def get(self, request, *args, **kwargs):
        member_id=kwargs.get('id')
        user=get_object_or_404(CustomUser, id=member_id)
        project = user.project
        user_skills = user.skills.all()  # Fetch the member's skills
        context = {
            'user': user,
            'project': project,
            'user_skills': user_skills,  # Pass the skills to the template
        }

        return render(request, 'member_profile.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Skill
from .forms import LeaderProfileForm
from django.core.mail import send_mail
from django.conf import settings

class LeaderProfileView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        project = user.project
        project_form = LeaderProfileForm()
        all_skills = Skill.objects.all()[:5]

        if project:
            occupied_with_current_project = CustomUser.objects.filter(
                project=project, user_type='member'
            )
        else:
            occupied_with_current_project = CustomUser.objects.none()

        context = {
            'user': user,
            'project': project,
            'project_form': project_form,
            'all_skills': all_skills,
            'occupied_with_current_project': occupied_with_current_project,
        }
        return render(request, 'leader_profile.html', context)

    def post(self, request, *args, **kwargs,):
        user = request.user

        if 'create_project' in request.POST:
            project_form = LeaderProfileForm(request.POST)
            if project_form.is_valid():
                project = project_form.save()
                user.project = project
                user.save()
                return redirect('leader_profile')
            else:
                print("invalid")
                print(project_form.errors.as_json())  # Print form errors for debugging

        elif 'delete_project' in request.POST:
            if user.project:
                user.project.delete()  # Delete the project from the database
                user.project = None
                user.save()
            return redirect('leader_profile')

        elif 'search_members' in request.POST:
            selected_skills_ids = request.POST.getlist('selected_skills')
            selected_skills_ids = [id for id in selected_skills_ids if id.isdigit()]
            if selected_skills_ids:
                selected_skills = Skill.objects.filter(id__in=selected_skills_ids)
                member_with_skills = CustomUser.objects.filter(skills__in=selected_skills, user_type='member').distinct()
                all_occupied_members = member_with_skills.filter(project__isnull=False).exclude(project=user.project)
                free_members = member_with_skills.filter(project__isnull=True)
            else:
                all_occupied_members = CustomUser.objects.none()
                free_members = CustomUser.objects.none()

            context = {
                'user': user,
                'project': user.project,
                'project_form': LeaderProfileForm(),
                'all_skills': Skill.objects.all()[:5],
                'occupied_with_current_project': CustomUser.objects.filter(project=user.project, 
                                                                           user_type='member',),
                'all_occupied_members': all_occupied_members,
                'free_members': free_members,
            }
            return render(request, 'leader_profile.html', context)

        elif 'send_emails' in request.POST:
            leader_email = request.POST.get('leader_email')
            free_members_emails = request.POST.getlist('free_members_emails')

            email_body = "\n".join(free_members_emails)
            send_mail(
                'List of Free Members',
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [leader_email],
                fail_silently=False,
            )
            return redirect('leader_profile')

        elif 'search_leader' in request.POST:
            search_query = request.POST.get('search_query')
            matching_leaders = CustomUser.objects.filter(username__icontains=search_query, user_type='leader')

            context = {
                'user': user,
                'project': user.project,
                'project_form': LeaderProfileForm(),
                'all_skills': Skill.objects.all()[:5],
                'matching_leaders': matching_leaders,
            }
            return render(request, 'leader_profile.html', context)

        elif 'remove_member' in request.POST:
            member_id = request.POST.get('member_id')
            if member_id:
                try:
                    member = CustomUser.objects.get(id=member_id, project=user.project, user_type='member')
                    member.project = None
                    member.save()
                except CustomUser.DoesNotExist:
                    pass  # Handle the case where the member does not exist or is not part of the project

            return redirect('leader_profile')

        elif 'add_member' in request.POST:
            member_id = request.POST.get('member_id')
            if member_id:
                try:
                    member = CustomUser.objects.get(id=member_id, project__isnull=True, user_type='member')
                    member.project = user.project
                    member.save()
                except CustomUser.DoesNotExist:
                    pass  # Handle the case where the member does not exist or is already part of a project

            return redirect('leader_profile')

        context = {
            'user': user,
            'project': user.project,
            'project_form': LeaderProfileForm(),
            'all_skills': Skill.objects.all()[:5],
            'occupied_with_current_project': CustomUser.objects.filter(project=user.project, user_type='member'),
        }
        return render(request, 'leader_profile.html', context)
    
def learn_skill(request):
    form = SkillSearchForm()
    videos = []
    skill = None
    query = None 
    
    if request.method == 'POST':
        form = SkillSearchForm(request.POST)
        if form.is_valid():
            skill = form.cleaned_data['skill']
            keyword = form.cleaned_data['keyword']
            if keyword:
                query = keyword
            else:
                query=skill
            videos = search_youtube(query)
    
    return render(request, 'learn_skill.html', {'form': form, 'videos': videos, 'skill': query})

def search_youtube(query):
    try:
        api_key = 'AIzaSyCrEnKkYXJrJApB3EjXBj9NadAVp_Oc6PQ'
        search_url = 'https://www.googleapis.com/youtube/v3/search'

        params = {
            'part': 'snippet',
            'q': query,
            'key': api_key,
            'maxResults': 10,
            'type': 'video'
        }

        response = requests.get(search_url, params=params)
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        results = response.json().get('items', [])

        videos = []
        for result in results:
            video_data = {
                'title': result['snippet']['title'],
                'url': f"https://www.youtube.com/watch?v={result['id']['videoId']}",
                'thumbnail': result['snippet']['thumbnails']['default']['url'],
            }
            videos.append(video_data)

        return videos

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []
