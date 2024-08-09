from django.contrib import admin
from userchat.models import GroupMessage, ChatGroup
# Register your models here.

admin.site.register(GroupMessage)
admin.site.register(ChatGroup)