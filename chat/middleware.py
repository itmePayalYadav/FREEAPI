from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from django.conf import settings
from accounts.models import User
import jwt

@database_sync_to_async
def get_user_from_payload(payload):
    uid = payload.get("user_id") or payload.get("user_id") or payload.get("user") or payload.get("id")
    if not uid:
        return None
    try:
        return User.objects.get(id=uid)
    except User.DoesNotExist:
        return None

class JwtAuthMiddleware(BaseMiddleware):
    """
    Expect token in query string: ?token=<jwt>
    Sets scope['user'] to authenticated user or AnonymousUser
    """
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        qs = parse_qs(query_string)
        token = None
        if "token" in qs:
            token = qs["token"][0]
        elif "access" in qs:
            token = qs["access"][0]

        if token:
            try:
                UntypedToken(token)
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = await get_user_from_payload(payload)
                scope['user'] = user
            except Exception:
                scope['user'] = None
        else:
            scope['user'] = None

        return await super().__call__(scope, receive, send)

def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(inner)
