import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Conversation, Message
from .ollama import stream_response
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data["message"]
        # fetch conversation and persist user's message
        try:
            conversation = await sync_to_async(Conversation.objects.get)(
                id=self.conversation_id
            )
        except Conversation.DoesNotExist:
            await self.close()
            return

        await sync_to_async(Message.objects.create)(
            conversation=conversation,
            role="user",
            content=user_message,
        )

        # prepare messages history for the model
        messages = [
            {"role": m.role, "content": m.content}
            for m in await sync_to_async(list)(conversation.messages.all())
        ]

        assistant_reply = ""

        # stream the AI response asynchronously and forward tokens to the client
        try:
            async for chunk in stream_response(messages):
                assistant_reply += chunk
                # send each token/chunk and mark as not-final
                await self.send(text_data=json.dumps({"token": chunk, "final": False}))
        except Exception as e:
            # if streaming fails, send an error message to the client
            await self.send(text_data=json.dumps({"error": "AI streaming failed: " + str(e), "final": True}))
        else:
            # after streaming completes, notify client the message is final
            await self.send(text_data=json.dumps({"token": "", "final": True}))

        # persist the full assistant reply
        await sync_to_async(Message.objects.create)(
            conversation=conversation,
            role="assistant",
            content=assistant_reply,
        )
