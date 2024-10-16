from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser

class Project(models.Model):
    name=models.CharField(max_length=100, unique= True) 
    def __str__(self) -> str:
        return self.name 
    
    def get_leader(self):
        # Retrieve the leader associated with this project
        return CustomUser.objects.filter(project=self, user_type='leader').first()
    
class Skill(models.Model):
    name=models.CharField(max_length=100, unique=True)
    search_keyword= models.CharField(max_length=100, help_text="keyword to search for videos to learn", blank=True)
    COMPETENCY_CHOICES=(
        ('novice','Novice'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('proficient', 'Proficient'),
        ('expert', 'Expert'),
    )
    competency=models.CharField(choices=COMPETENCY_CHOICES, max_length=20)

    def __str__(self) -> str:
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        email=self.normalize_email(email)
        user=self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        print(f"User {username} created successfully.")
        return user
    
    def create_superuser(self, username, email , password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin',True)
        is_admin = models.BooleanField(default=True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('superuser must have is_admin=True')
        print(f"Superuser {username} created successfully.")
        return self.create_superuser(username, email,password, **extra_fields)
    
class CustomUser(AbstractUser):
    ROLE_CHOICE=(
        ('member','Member'),
        ('leader', 'leader'),
    )
    user_type=models.CharField(max_length=20,choices=ROLE_CHOICE)
    username=models.CharField(max_length=150,unique=True,error_messages={'unique':'A user with this username already exists'})
    is_admin = models.BooleanField(default=False)
    skills=models.ManyToManyField(Skill, blank=True,related_name='users')
    project=models.ForeignKey(Project, on_delete=models.SET_NULL, related_name='project', null=True, blank=True)

    def is_member(self):
        return self.user_type=='member'
    def is_leader(self):
        return self.user_type=='leader'
    
    objects=CustomUserManager()


 