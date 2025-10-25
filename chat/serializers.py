from rest_framework import serializers
from .models import Chat, ChatParticipant, Message
from accounts.models import User

class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "avatar")

class ChatParticipantSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    class Meta:
        model = ChatParticipant
        fields = ("user","role","joined_at")

class ChatListSerializer(serializers.ModelSerializer):
    participants = ChatParticipantSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ("id","name","chat_type","owner","participants","last_message","updated_at")

    def get_last_message(self, obj):
        if obj.last_message:
            return {
                "id": str(obj.last_message.id),
                "content": obj.last_message.content,
                "sender_id": getattr(obj.last_message.sender, "id", None),
                "created_at": obj.last_message.created_at.isoformat()
            }
        return None

class ChatCreateSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(child=serializers.UUIDField(), required=False)

    class Meta:
        model = Chat
        fields = ("id","name","chat_type","member_ids")

class MessageSerializer(serializers.ModelSerializer):
    sender = UserBriefSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ("id","chat","sender","content","attachment","created_at","edited_at")
        read_only_fields = ("sender","created_at","edited_at")
