from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation


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

    return render(request, "chat/chat.html", {
        "conversation_id": conversation.id
    })
