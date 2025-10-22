import uuid
from django.db import models
from django.utils import timezone

# ===============================
# SOFT DELETE MANAGER
# ===============================
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, deleted_at__isnull=True)

# ===============================
# BASE MODEL
# ===============================
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager() 
    all_objects = models.Manager()

    class Meta:
        abstract = True

    # ----------------------------
    # Methods
    # ----------------------------
    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at'])

    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_active', 'deleted_at'])

    def delete(self, hard=False, *args, **kwargs):
        if hard:
            super().delete(*args, **kwargs)
        else:
            self.soft_delete()
