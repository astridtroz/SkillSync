# forms.py
from django import forms
from .models import Assignment, Video, Progress
from django.core.exceptions import ValidationError
from dashboard.models import *
class CreateAssignmentForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if project:
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(project=project, user_type='member')  

    class Meta:
        model = Assignment
        fields = ['title', 'assigned_to'] 

class ProgressForm(forms.Form):
    watched_seconds = forms.IntegerField(min_value=0, required=True)
