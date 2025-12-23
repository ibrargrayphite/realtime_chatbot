from django.urls import path
from .views import chat_view, create_new_chat, SignUpView

urlpatterns = [
    path("", create_new_chat, name="new_chat"),
    path("chat/<int:conversation_id>/", chat_view, name="chat"),
    path('signup/', SignUpView.as_view(), name='signup'),
]
