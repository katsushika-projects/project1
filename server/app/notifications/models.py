from uuid import uuid4

from django.conf import settings
from django.db import models


class Notification(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        read_status = "Read" if self.is_read else "Unread"
        importance = "Important" if self.is_important else "Normal"
        return f"[{read_status}] [{importance}] {self.title} - {self.user.email}"
