from django.urls import path
from . import views
import logging
from .views import NominateMemberView


logger = logging.getLogger(__name__)

urlpatterns = [
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('calendar/events/', views.get_events, name='get_events'),
    path('calendar/create-event/', views.create_event, name='create_event'),
    path('calendar/delete-event/', views.delete_event, name='delete_event'),
    path('nominate-member/<int:event_id>/', NominateMemberView.as_view(), name='nominate_member'),
    path('calendar/handle-nomination/', views.handle_nomination, name='handle_nomination'),
    path('calendar/get-members/', views.get_members, name='get_members'),
    path('calendar/get-nominations/<int:event_id>/', views.get_nominations, name='get_nominations'),
]
