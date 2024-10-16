# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_assignment, name='create_assignment'),
    path('search/', views.search_videos_view, name='search_videos'),
    path('assignments/', views.view_assignments, name='view_assignments'),
    path('assignments/<int:assignment_id>/progress/', views.view_progress, name='view_progress'),
]
