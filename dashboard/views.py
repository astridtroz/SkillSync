from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.viewsets import ModelViewSet
from django.contrib import messages
from .models import CustomUser, Skill
from .forms import RegistrationForm, LoginForm, SkillAddForm, LeaderProfileForm,CustomPasswordResetForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import PasswordResetView

# Create your views here.


def welcome(request):
    return render(request, 'index.html')

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
                   return redirect('member_profile')
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
            return redirect('login')  # Redirect if the user is not logged in

        search_query = request.GET.get('search', '')
        all_skills = Skill.objects.all()
        
        if search_query:
            available_skills = all_skills.filter(name__icontains=search_query)
        else:
            available_skills = all_skills[:4]  # Show only a limited number of skills
        
        user_skills = user.skills.all()  # Assuming a ManyToManyField for skills

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
            return redirect('login')  # Redirect if the user is not logged in

        if 'add_skill' in request.POST:
            form = SkillAddForm(request.POST)
            if form.is_valid():
                new_skill_name = form.cleaned_data['name']
                skill, created = Skill.objects.get_or_create(name=new_skill_name)

                if created:
                    messages.success(request, f'New skill "{new_skill_name}" added successfully.')
                else:
                    messages.info(request, f'Skill "{new_skill_name}" already exists.')

                # Associate new skill with the user
                user.skills.add(skill)
                user.save()

        if 'update_skills' in request.POST:
            selected_skill_ids = request.POST.getlist('skills')
            selected_skills = Skill.objects.filter(id__in=selected_skill_ids)
            for skill in selected_skills:
                user.skills.add(skill)
            user.save()
            messages.success(request, 'Skills updated successfully.')

        if 'delete_skill' in request.POST:
            skill_id = request.POST.get('delete_skill')
            skill_to_delete = Skill.objects.get(id=skill_id)
            user.skills.remove(skill_to_delete)
            user.save()
            messages.success(request, f'Skill "{skill_to_delete.name}" removed successfully.')

        return redirect('manage_skills')


class MemberProfileView(View):
    def get(self,request,*args, **kwargs):
        user=request.user
        project=user.project
        context={
            'user':user,
            'project':project,
        }

        return render(request, 'member_profile.html', context)




class LeaderProfileView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        project = user.project
        project_form = LeaderProfileForm()
        all_skills = Skill.objects.all()[:5]
        context = {
            'user': user,
            'project': project,
            'project_form': project_form,
            'all_skills': all_skills,
        }
        return render(request, 'leader_profile.html', context)

    def post(self, request, *args, **kwargs):
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
            # Filter out empty strings and ensure IDs are integers
            selected_skills_ids = [id for id in selected_skills_ids if id.isdigit()]
            if selected_skills_ids:
                selected_skills = Skill.objects.filter(id__in=selected_skills_ids)
                member_with_skills = CustomUser.objects.filter(skills__in=selected_skills).distinct()
                occupied_members = member_with_skills.filter(project__isnull=False)
                free_members = member_with_skills.filter(project__isnull=True)
            else:
                occupied_members = CustomUser.objects.none()
                free_members = CustomUser.objects.none()

            context = {
                'user': user,
                'project': user.project,
                'project_form': LeaderProfileForm(),
                'all_skills': Skill.objects.all()[:5],
                'occupied_members': occupied_members,
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
            matching_leaders = CustomUser.objects.filter(username__icontains=(search_query))

            context = {
                'user': user,
                'project': user.project,
                'project_form': LeaderProfileForm(),
                'all_skills': Skill.objects.all()[:5],
                'matching_leaders': matching_leaders,
            }
            return render(request, 'leader_profile.html', context)

        # If none of the conditions match, re-render the form
        context = {
            'user': user,
            'project': user.project,
            'project_form': LeaderProfileForm(),
            'all_skills': Skill.objects.all()[:5],
        }
        return render(request, 'leader_profile.html', context)





class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
