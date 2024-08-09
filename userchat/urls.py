from django.urls import path
from userchat.views import *

urlpatterns=[
    path('', chat_view, name="chat"),
    path('chat/<username>', get_or_create_chatroom, name="start-chat"),
    path('chat/room/<chatroom_name>', chat_view, name="chatroom"),
    path('chat/group/<int:project_id>/', get_group_chat, name='team_chat'),
]