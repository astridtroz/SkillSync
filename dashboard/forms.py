from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import password_validation
from .models import CustomUser, Skill, Project

class RegistrationForm(UserCreationForm):
    email=forms.EmailField(required=True)
    password1=forms.CharField(
        label="Password",
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2=forms.CharField(
        label="Confirm Password",
    )
    class Meta:
        model= CustomUser
        fields=('username','email','user_type')

class LoginForm(forms.Form):
    username=forms.CharField(max_length=255)
    password=forms.CharField(max_length=255)
    class Meta:
        model= CustomUser
        fields=('username','password','email')

class SkillAddForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']

    name = forms.CharField(label='New Skill', max_length=100, required=True)

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

    