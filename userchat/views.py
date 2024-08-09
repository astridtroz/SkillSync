from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import ChatGroup
from .forms import ChatmessageCreateForm
from dashboard.models import *
@login_required
def chat_view(request, chatroom_name='public-chat'):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatmessageCreateForm()
    
    other_user=None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user=member
                break

    if request.method == 'POST':
        print("post req recieved")
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            print("valid form")
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            print("Preparing to save message:", message.body)  # Debugging line
            message.save()
            print("Message saved successfully!")
            
            if request.htmx:
                context = {
                    'message': message,
                    'user': request.user,
                }
                return render(request, 'userchat/partial/chat_message_p.html', context)
            else:
                # If not an HTMX request, redirect to avoid form resubmission on refresh
                return redirect('chat_view')
        else:
            print("Form errors:", form.errors)  # Debugging line to check form errors
    context={
        'chat_messages': chat_messages,
        'form': form,
        'other_user' : other_user,
        'chatroom_name': chatroom_name,
    }
    return render(request, 'userchat/chat.html', context)

@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username: #same user chat req
        return redirect('chat')           #redirect to chat page with himself only
    
    other_user=CustomUser.objects.get(username=username) #we get other user
    my_chatrooms=request.user.chat_groups.filter(is_private=True)

    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                chatroom=chatroom
                break
            else:
                chatroom=ChatGroup.objects.create(is_private=True)
                chatroom.members.add(other_user, request.user)
    else:
        chatroom=ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user, request.user)
    
    return redirect('chatroom', chatroom.group_name)

@login_required
def get_group_chat(request, project_id):
    project=get_object_or_404(Project,id=project_id)
    all_users=CustomUser.objects.all()
    all_members=all_users.filter(project=project)

    group_chat_name=f'group_chat_{project.name}'

    chatroom, created=ChatGroup.objects.get_or_create(group_name=group_chat_name, is_private=False)

    if created:
        chatroom.members.add(all_members)
    
    return redirect('chatroom',chatroom.group_name)




