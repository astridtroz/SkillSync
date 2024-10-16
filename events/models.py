# myapp/models.py
from django.db import models
from django.conf import settings
from dashboard.models import *
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # Additional fields

class MemberNomination(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    leader = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    member = models.ForeignKey(CustomUser, related_name='nominations', on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
