# views.py
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

class NotificationViewSet(ReadOnlyModelViewSet):
    queryset = Notification.objects.order_by("-published_at")
    serializer_class = NotificationSerializer

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.read = True
        notif.save()
        return Response({"status": "marked as read"})