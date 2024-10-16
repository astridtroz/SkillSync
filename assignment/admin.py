# admin.py
from django.contrib import admin
from .models import Assignment, Video, Progress, Notification

admin.site.register(Assignment)
admin.site.register(Video)
admin.site.register(Progress)
admin.site.register(Notification)
