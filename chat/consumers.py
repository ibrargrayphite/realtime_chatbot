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

        # stream the AI response asynchronously and forward parsed tokens to the client
        try:
            async for chunk in stream_response(messages):
                # chunk is expected to be a JSON string per-line from the model server
                content_piece = ""
                try:
                    parsed = json.loads(chunk)
                except Exception:
                    # not JSON — forward raw chunk
                    content_piece = chunk
                else:
                    # prefer nested message.content (Ollama style), then common fields
                    if isinstance(parsed, dict):
                        if parsed.get("message") and isinstance(parsed.get("message"), dict):
                            content_piece = parsed.get(
                                "message", {}).get("content", "")
                        else:
                            content_piece = (
                                parsed.get("token")
                                or parsed.get("text")
                                or parsed.get("content")
                                or (parsed.get("delta") and parsed.get("delta").get("content"))
                                or ""
                            )

                        # if the model signals completion with a `done` flag, stop streaming
                        if parsed.get("done"):
                            # send any final content piece then break
                            if content_piece:
                                assistant_reply += content_piece
                                await self.send(text_data=json.dumps({"token": content_piece, "final": False}))
                            await self.send(text_data=json.dumps({"token": "", "final": True}))
                            break

                if content_piece:
                    assistant_reply += content_piece
                    await self.send(text_data=json.dumps({"token": content_piece, "final": False}))
        except Exception as e:
            await self.send(text_data=json.dumps({"error": "AI streaming failed: " + str(e), "final": True}))

        # persist the full assistant reply
        await sync_to_async(Message.objects.create)(
            conversation=conversation,
            role="assistant",
            content=assistant_reply,
        )
