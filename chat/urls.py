from django.urls import path
from .views import chat_view, create_new_chat

urlpatterns = [
    path("chat/new/", create_new_chat, name="new_chat"),
    path("chat/<int:conversation_id>/", chat_view, name="chat"),
]
