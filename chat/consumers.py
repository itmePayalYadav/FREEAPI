import json
from channels.generic.websocket import AsyncWebsocketConsumer
from accounts.models import User
from chat.models import Message
from channels.db import database_sync_to_async

online_users = set() 

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            self.user.username = f"guest_{self.username}"

        self.room_group_name = f"chat_{min(self.user.username, self.username)}_{max(self.user.username, self.username)}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        online_users.add(self.user.username)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        online_users.discard(self.user.username)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        if not message:
            return

        receiver = await database_sync_to_async(User.objects.get)(username=self.username)
        msg_obj = await database_sync_to_async(Message.objects.create)(
            sender=self.user,
            receiver=receiver,
            text=message
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
                'timestamp': str(msg_obj.timestamp),
                'is_read': msg_obj.is_read
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
