from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Chat, ChatParticipant, Message
from .serializers import ChatListSerializer, ChatCreateSerializer, MessageSerializer, UserBriefSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.CreateModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = Chat.objects.all()

    def get_serializer_class(self):
        if self.action in ("list","retrieve"):
            return ChatListSerializer
        return ChatCreateSerializer

    def get_queryset(self):
        return Chat.objects.filter(participants__user=self.request.user, participants__is_active=True).distinct()

    def perform_create(self, serializer):
        with transaction.atomic():
            chat = serializer.save(owner=self.request.user)
            # add creator
            ChatParticipant.objects.create(chat=chat, user=self.request.user, role="admin")
            member_ids = self.request.data.get("member_ids", [])
            for uid in member_ids:
                if str(uid) == str(self.request.user.id): 
                    continue
                ChatParticipant.objects.create(chat=chat, user_id=uid)

    @action(detail=False, methods=["get"])
    def available_users(self, request):
        qs = User.objects.exclude(id=request.user.id)[:100]
        return Response(UserBriefSerializer(qs, many=True).data)

    @action(detail=False, methods=["post"])
    def one_on_one(self, request):
        target_id = request.data.get("target_user_id")
        if not target_id:
            return Response({"detail":"target_user_id required"}, status=400)
        # search existing private chat with exactly these 2 participants
        chats = Chat.objects.filter(chat_type="private", participants__user=request.user).distinct()
        for c in chats:
            ids = set(c.participants.values_list("user_id", flat=True))
            if ids == {request.user.id, int(target_id)}:
                return Response(ChatListSerializer(c).data)
        # create private chat
        with transaction.atomic():
            chat = Chat.objects.create(chat_type="private")
            ChatParticipant.objects.create(chat=chat, user=request.user, role="admin")
            ChatParticipant.objects.create(chat=chat, user_id=target_id)
        return Response(ChatListSerializer(chat).data, status=201)

    @action(detail=True, methods=["post"])
    def add_participant(self, request, pk=None):
        chat = get_object_or_404(Chat, pk=pk)
        uid = request.data.get("user_id")
        ChatParticipant.objects.update_or_create(chat=chat, user_id=uid, defaults={"is_active": True})
        return Response(ChatListSerializer(chat).data)

    @action(detail=True, methods=["delete"])
    def leave(self, request, pk=None):
        chat = get_object_or_404(Chat, pk=pk)
        ChatParticipant.objects.filter(chat=chat, user=request.user).update(is_active=False)
        return Response(status=204)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.request.query_params.get("chat")
        qs = Message.objects.filter(chat_id=chat_id, is_active=True).order_by("-created_at")
        return qs

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
