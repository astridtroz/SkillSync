from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Skill, Project

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_admin')
    list_filter = ('is_admin',)
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ()

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Skill)
admin.site.register(Project)

