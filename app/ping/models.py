import uuid
from django.db import models

class PingLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_pinged_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ping_log'
