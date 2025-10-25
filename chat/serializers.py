from rest_framework import serializers
from chat.models import Message

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    receiver = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = "__all__"