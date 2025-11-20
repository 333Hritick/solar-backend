from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import json
import random

class EnergyConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("CLIENT CONNECTED")
        await self.accept()

        self.active = True
        self.loop_task = asyncio.create_task(self.stream_data())

    async def disconnect(self, close_code):
        print("CLIENT DISCONNECTED")
        self.active = False
        if hasattr(self, "loop_task"):
            self.loop_task.cancel()

    async def stream_data(self):
        while self.active:
            data = {
                "production": round(random.uniform(40, 50), 1),
                "consumption": round(random.uniform(30, 35), 1),
                "surplus": round(random.uniform(10, 15), 1),
                "credits": round(random.uniform(150, 160), 2)
            }

            await self.send(json.dumps(data))
            await asyncio.sleep(2)
