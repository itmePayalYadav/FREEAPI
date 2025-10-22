from rest_framework import permissions

# ===============================
# Role-based Permission Base
# ===============================
class RolePermission(permissions.BasePermission):
    def __init__(self, roles=None):
        self.roles = roles or []

    def has_permission(self, request, view):
        return bool(
            request.user 
            and request.user.is_authenticated 
            and request.user.role in self.roles
        )

# ===============================
# SUPERADMIN Only
# ===============================
class IsSuperAdmin(RolePermission):
    def __init__(self):
        super().__init__(roles=["SUPERADMIN"])
        self.message = "Only SUPERADMIN can perform this action."

# ===============================
# ADMIN or SUPERADMIN
# ===============================
class IsAdminOrSuperAdmin(RolePermission):
    def __init__(self):
        super().__init__(roles=["ADMIN", "SUPERADMIN"])
        self.message = "Only ADMIN or SUPERADMIN can perform this action."

# ===============================
# Any Authenticated User (USER, ADMIN, SUPERADMIN)
# ===============================
class IsAuthenticatedUser(permissions.BasePermission):
    message = "Authentication required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

# ===============================
# Owner or Admin/SUPERADMIN
# ===============================
class IsOwnerOrAdmin(permissions.BasePermission):
    message = "You must be the owner or an admin to perform this action."

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "author", None) or getattr(obj, "user", None)
        return bool(owner == request.user or request.user.role in ["ADMIN", "SUPERADMIN"])
