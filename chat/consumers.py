import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message, ChatParticipant
from accounts.models import User

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"].get("chat_id")
        self.group_name = f"chat_{self.chat_id}"

        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close(code=4001)
            return

        allowed = await self.user_in_chat(user.id, self.chat_id)
        if not allowed:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # optionally broadcast presence
        await self.channel_layer.group_send(self.group_name, {
            "type": "presence",
            "user_id": str(user.id),
            "action": "joined"
        })

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        user = self.scope.get("user")
        if user and getattr(user, "is_authenticated", False):
            await self.channel_layer.group_send(self.group_name, {
                "type": "presence",
                "user_id": str(user.id),
                "action": "left"
            })

    async def receive_json(self, content, **kwargs):
        """
        Expected actions:
        { type: "send_message", content: "hello" }
        { type: "typing", active: true }
        { type: "mark_read", message_id: "<uuid>" }
        """
        event_type = content.get("type")
        user = self.scope["user"]

        if event_type == "send_message":
            text = content.get("content", "").strip()
            if not text and not content.get("attachment"):
                return
            msg = await self.create_message(self.chat_id, user.id, text, content.get("attachment"))
            payload = {
                "type": "new_message",
                "message": {
                    "id": str(msg.id),
                    "chat": str(self.chat_id),
                    "sender": {"id": str(user.id), "username": user.username},
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
            }
            await self.channel_layer.group_send(self.group_name, {
                "type": "broadcast",
                "payload": payload
            })

        elif event_type == "typing":
            await self.channel_layer.group_send(self.group_name, {
                "type": "broadcast",
                "payload": {"type":"typing","user_id": str(user.id), "active": content.get("active", True)}
            })

        elif event_type == "mark_read":
            message_id = content.get("message_id")
            await self.mark_read(message_id, user.id)
            # optionally broadcast read receipt

    async def broadcast(self, event):
        payload = event.get("payload")
        await self.send_json(payload)

    async def presence(self, event):
        await self.send_json({"type":"presence","user_id": event.get("user_id"), "action": event.get("action")})

    @database_sync_to_async
    def user_in_chat(self, user_id, chat_id):
        return ChatParticipant.objects.filter(chat_id=chat_id, user_id=user_id, is_active=True).exists()

    @database_sync_to_async
    def create_message(self, chat_id, sender_id, content, attachment=None):
        chat = Chat.objects.get(id=chat_id)
        msg = Message.objects.create(chat=chat, sender_id=sender_id, content=content)
        return msg

    @database_sync_to_async
    def mark_read(self, message_id, user_id):
        try:
            msg = Message.objects.get(id=message_id)
            msg.read_by.add(user_id)
            return True
        except Message.DoesNotExist:
            return False
