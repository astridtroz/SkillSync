# models.py
from django.db import models
from dashboard.models import CustomUser
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class Video(models.Model):
    youtube_id = models.CharField(max_length=11, unique=True, blank=True)
    title = models.CharField(max_length=255)
    youtube_url = models.URLField()
    duration = models.PositiveIntegerField()  # Duration in seconds

    def __str__(self):
        return self.title

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    videos = models.ManyToManyField(Video)
    created_by = models.ForeignKey(CustomUser, related_name='created_assignments', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(CustomUser, related_name='assignments', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed=models.BooleanField(default=False)
    def __str__(self):
        return self.title

class Progress(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched_seconds = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.member.username} - {self.assignment.title} - {self.video.title}"

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def send_email(self):
        subject = 'Assignment Completed'
        html_message = render_to_string('notification_email.html', {'message': self.message})
        plain_message = strip_tags(html_message)
        from_email = 'noreply@example.com'
        to_email = [self.user.email]
        send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
