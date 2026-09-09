# notifications/models.py
from django.db import models
from django.conf import settings

class Notification(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    source = models.CharField(max_length=255)  # e.g., MNRE, PM Surya Ghar
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)   # ✅ new field
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # optional per-user

    def __str__(self):
        return self.title
