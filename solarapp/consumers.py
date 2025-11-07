import json
import random
from asyncio import sleep
from channels.generic.websocket import AsyncWebsocketConsumer

class EnergyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # send random energy data every 3 seconds
        while True:
            data = {
                "production": round(random.uniform(40, 60), 2),
                "consumption": round(random.uniform(25, 45), 2),
                "surplus": round(random.uniform(10, 20), 2),
                "credits": round(random.uniform(100, 200), 2),
            }
            await self.send(json.dumps(data))
            await sleep(3)
