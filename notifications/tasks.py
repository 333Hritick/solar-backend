# notifications/tasks.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from celery import shared_task
from django.utils import timezone
from .models import Notification

@shared_task(name="fetch_mnre_updates_task")
def fetch_mnre_updates_task():
    notices = [
        {"title": "Solar Subsidy Update", "content": "New subsidy announced", "source": "MNRE"}
    ]

    channel_layer = get_channel_layer()

    for n in notices:
        notif = Notification.objects.create(
            title=n["title"],
            content=n["content"],
            source=n["source"],
            published_at=timezone.now()   # ✅ fixes IntegrityError
        )

        print("Broadcasting:", notif.title)

        async_to_sync(channel_layer.group_send)(
            "notifications",
            {
                "type": "new_notification",
                "title": notif.title,
                "content": notif.content,
                "source": notif.source,
                "published_at": notif.published_at.isoformat(),
            }
        )
