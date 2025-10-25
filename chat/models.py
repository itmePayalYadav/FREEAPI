import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from accounts.models import User  
from core.models import BaseModel
from core.constants import CHAT_TYPES, CHAT_ROLE_CHOICES

# =============================================================
# CHAT MODEL
# =============================================================
class Chat(BaseModel):
    name = models.CharField(max_length=200, blank=True)
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPES, default='private')
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='owned_chats')
    last_message = models.ForeignKey('Message', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    class Meta:
        db_table = 'chat_chats'
        ordering = ('-updated_at',)

    def __str__(self):
        return f"{self.chat_type.title()} Chat: {self.name or self.id}"

    @property
    def participant_count(self):
        return self.participants.count()


# =============================================================
# CHAT PARTICIPANT MODEL
# =============================================================
class ChatParticipant(BaseModel):
    chat = models.ForeignKey(Chat, related_name='participants', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='chat_participations', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=CHAT_ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'chat_participants'
        unique_together = ('chat', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.chat}"

    def is_admin(self):
        return self.role == 'admin'


# =============================================================
# MESSAGE MODEL
# =============================================================
class Message(BaseModel):
    chat = models.ForeignKey(Chat, related_name='messages',on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.SET_NULL, null=True)
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ('created_at',)

    def __str__(self):
        return f"Message from {self.sender} in {self.chat}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.chat:
            self.chat.last_message = self
            self.chat.save(update_fields=['last_message', 'updated_at'])
