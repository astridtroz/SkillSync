from django.urls import path, include
from dashboard import views
from .views import ManageSkillsView, LeaderProfileView, MemberProfileView

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('home/',views.home_view, name='home'),
    path('logout/',views.user_logout, name='logout'),
    path('skills/', ManageSkillsView.as_view(), name='manage_skills'),
    path('member_profile/', MemberProfileView.as_view(), name='member_profile'),
    path('leader_profile/', LeaderProfileView.as_view(), name='leader_profile'),
]