from django.urls import path
from .views import (
    chat_view,
    create_new_chat,
    SignUpView,
    conversations_list,
    edit_conversation,
    delete_conversation,
)

urlpatterns = [
    path("", conversations_list, name="conversations"),
    path("chat/new/", create_new_chat, name="new_chat"),
    path("chat/<int:conversation_id>/", chat_view, name="chat"),
    path("chat/<int:conversation_id>/edit/",
         edit_conversation, name="edit_conversation"),
    path("chat/<int:conversation_id>/delete/",
         delete_conversation, name="delete_conversation"),
    path('signup/', SignUpView.as_view(), name='signup'),
]
