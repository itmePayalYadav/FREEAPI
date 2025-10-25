from rest_framework import viewsets
from chat.models import Message
from chat.serializers import MessageSerializer
from accounts.models import User
from core.permissions import IsAuthenticatedUser
from core.utils import api_response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedUser]
    lookup_field = "pk"

    def get_queryset(self):
        username = self.request.query_params.get("username")
        if username:
            try:
                other_user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Message.objects.none()

            return Message.objects.filter(
                sender__in=[self.request.user, other_user],
                receiver__in=[self.request.user, other_user]
            ).order_by("timestamp")
        return Message.objects.filter(sender=self.request.user).order_by("timestamp")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(True, "Messages retrieved successfully", serializer.data)

    def create(self, request, *args, **kwargs):
        receiver_username = request.data.get("receiver")
        text = request.data.get("text")

        if not receiver_username or not text:
            return api_response(False, "Receiver and text are required", status=400)

        try:
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            return api_response(False, "Receiver not found", status=404)

        message = Message.objects.create(sender=request.user, receiver=receiver, text=text)

        # Send via WebSocket
        channel_layer = get_channel_layer()
        room_group_name = f"chat_{min(request.user.username, receiver.username)}_{max(request.user.username, receiver.username)}"
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "chat_message",
                "message": message.text,
                "sender": request.user.username,
                "timestamp": str(message.timestamp),
                "is_read": message.is_read
            }
        )

        serializer = self.get_serializer(message)
        return api_response(True, "Message sent successfully", serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            message = Message.objects.get(pk=kwargs.get("pk"))
        except Message.DoesNotExist:
            return api_response(False, "Message not found", status=404)

        if message.sender != request.user and message.receiver != request.user:
            return api_response(False, "Not allowed to delete this message", status=403)

        message.delete()
        return api_response(True, "Message deleted successfully")
