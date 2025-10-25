from rest_framework import routers
from chat.views import ChatViewSet, MessageViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r"chats", ChatViewSet, basename="chats")
router.register(r"messages", MessageViewSet, basename="messages")

urlpatterns = [
    path("", include(router.urls)),
]
