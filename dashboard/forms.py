from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import password_validation
from .models import CustomUser, Skill, Project
from django_recaptcha.fields import ReCaptchaField

class RegistrationForm(UserCreationForm):
    captcha = ReCaptchaField()
    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.TextInput(attrs={'type': 'text'}),  # Confirm password visible
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'captcha')

class LoginForm(forms.Form):
    captcha = ReCaptchaField()
    username=forms.CharField(max_length=255)
    password=forms.CharField(max_length=255,
                              widget=forms.PasswordInput(),
                             )
    class Meta:
        model= CustomUser
        fields=('username','password','email','captcha')

class SkillAddForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'competency']

    name = forms.CharField(label='New Skill', max_length=100, required=True)
    competency=forms.ChoiceField(choices=Skill.COMPETENCY_CHOICES, label='Competency Level')

from django import forms
from .models import Project

class LeaderProfileForm(forms.ModelForm):
    name = forms.CharField(label='Project Name', max_length=100, required=True)

    class Meta:
        model = Project
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Project.objects.filter(name=name).exists():
            raise forms.ValidationError("Project with this Name already exists.")
        return name


class LeaderProfileForm(forms.ModelForm):
    name = forms.CharField(label='Project Name', max_length=100, required=True)

    class Meta:
        model = Project
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Project.objects.filter(name=name).exists():
            raise forms.ValidationError("Project with this Name already exists.")
        return name

from django.contrib.auth.forms import PasswordResetForm

class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        # Customize email sending here
        super().send_mail(subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name)

SKILL_CHOICES = [
    ('python', 'Python'),
    ('java', 'Java'),
    ('javascript', 'JavaScript'),
]
class SkillSearchForm(forms.Form):
    skill = forms.ChoiceField(choices=SKILL_CHOICES, label="Skill")
    keyword = forms.CharField(required=False, label="Search for a skill", widget=forms.TextInput(attrs={'placeholder': 'Search for a skill...'}))