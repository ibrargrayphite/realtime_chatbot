from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation
from .forms import UserSignUpForm
from django.contrib.auth import login
from django.views import View


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

    return render(request, "chat/chat.html", {
        "conversation_id": conversation.id
    })
