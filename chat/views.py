from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation
from .forms import UserSignUpForm
from django.contrib.auth import login
from django.views import View
from django.http import HttpResponseForbidden


class SignUpView(View):
    def get(self, request):
        form = UserSignUpForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('new_chat')
        return render(request, 'registration/signup.html', {'form': form})


@login_required
def create_new_chat(request):
    conversation = Conversation.objects.create(
        user=request.user,
        title="New Chat"
    )
    return redirect("chat", conversation_id=conversation.id)


@login_required
def chat_view(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user
    )
    # load messages ordered by creation time so we can render history
    messages = conversation.messages.order_by('created_at')

    return render(request, "chat/chat.html", {
        "conversation_id": conversation.id,
        "messages": messages,
    })


@login_required
def conversations_list(request):
    """List all conversations for the current user."""
    conversations = Conversation.objects.filter(
        user=request.user).order_by('-created_at')
    return render(request, 'chat/conversations.html', {
        'conversations': conversations,
    })


@login_required
def edit_conversation(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            conversation.title = title
            conversation.save()
            return redirect('conversations')
        # if title empty, re-render with an error
        return render(request, 'chat/edit_conversation.html', {
            'conversation': conversation,
            'error': 'Title cannot be empty.'
        })

    return render(request, 'chat/edit_conversation.html', {
        'conversation': conversation,
    })


@login_required
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user)
    if request.method == 'POST':
        conversation.delete()
        return redirect('conversations')
    return render(request, 'chat/confirm_delete.html', {
        'conversation': conversation,
    })
