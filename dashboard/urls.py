from django.urls import path, include
from dashboard import views
from django.contrib.auth import views as auth_views
from .views import *
urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('accounts/login/', views.login_view, name='login'),
    path('home/',views.home_view, name='home'),
    path('logout/',views.user_logout, name='logout'),
    path('skills/', ManageSkillsView.as_view(), name='manage_skills'),
    path('member_profile/<int:id>/', MemberProfileView.as_view(), name='member_profile'),
    path('leader_profile/', LeaderProfileView.as_view(), name='leader_profile'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('chat/', include('userchat.urls')),
    path('learn-skill/', views.learn_skill, name='learn_skill'),

]