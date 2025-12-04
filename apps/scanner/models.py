from django.db import models
from django.utils import timezone
import uuid

class PagesSpeedTests(models.Model):
    site_url = models.URLField()
    user_ip = models.GenericIPAddressField()
    created_at = models.DateTimeField(default=timezone.now)
    result_file = models.FilePathField(path='data', recursive=True)
    access_link = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"{self.site_url} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
