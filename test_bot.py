import requests

BOT_TOKEN ="8084652463:AAGUVvnvNoNMQmEocqpROaFKqgHgP-C86ho"
CHAT_ID = "5698737028"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {"chat_id": CHAT_ID, "text": "Hello! Test message from Python"}

response = requests.post(url, data=data)
print(response.json())
