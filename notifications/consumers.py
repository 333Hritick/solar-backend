# notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self,event):
        print("Consumer received:", event)
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

        # Send a test message immediately
       

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def new_notification(self, event):
        await self.send(text_data=json.dumps(event))
