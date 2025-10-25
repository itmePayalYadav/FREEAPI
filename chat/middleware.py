import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from accounts.models import User

@database_sync_to_async
def get_user_from_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        return User.objects.get(id=user_id)
    except Exception:
        return AnonymousUser()

class JwtAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return JwtAuthMiddlewareInstance(scope, self.inner)

class JwtAuthMiddlewareInstance:
    def __init__(self, scope, inner):
        self.scope = dict(scope)
        self.inner = inner

    async def __call__(self, receive, send):
        query_string = self.scope.get("query_string", b"").decode()
        token = None
        if "token=" in query_string:
            token = query_string.split("token=")[1].split("&")[0]

        self.scope["user"] = await get_user_from_token(token) if token else AnonymousUser()

        inner = self.inner(self.scope)
        return await inner(receive, send)

def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(inner)
