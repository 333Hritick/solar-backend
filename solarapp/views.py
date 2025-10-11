from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import QuoteRequest
from .serializers import QuoteRequestSerializer
import requests
from django.http import JsonResponse

TELEGRAM_BOT_TOKEN = "8084652463:AAGUVvnvNoNMQmEocqpROaFKqgHgP-C86ho"
TELEGRAM_CHAT_ID = "5698737028"

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=data)
    return response.json()


@api_view(['POST'])
def create_quote(request):
    serializer = QuoteRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        quote = serializer.save()  # Save instance

        # Prepare Telegram message
        message = (
            f"📩 New Quote Request!\n\n"
            f"👤 Name: {quote.name}\n"
            f"📧 Email: {quote.email}\n"
            f"📞 Phone: {quote.phone}\n"
            f"🏙️ District: {quote.district}\n"
            f"💵 Monthly Bill: {quote.monthlyBill}\n"
            f"🏠 Rooftop Area: {quote.rooftopArea}\n"
            f"💬 Message: {quote.message or 'N/A'}\n"
            f"🕒 Submitted at: {quote.created_at.strftime('%Y-%m-%d %H:%M:%S') if quote.created_at else 'N/A'}"
        )

        # Send Telegram safely
        try:
            send_telegram_message(message)
        except Exception as e:
            # Log the error, but don’t crash the API
            print(f"Telegram error: {e}")

        return Response(
            {"message": "Quote request submitted successfully!"},
            status=status.HTTP_201_CREATED
        )
       
    else:
        # Return serializer errors
        return Response(
           serializer.errors,
           status=status.HTTP_400_BAD_REQUEST
        )


def home(request):
    return JsonResponse({"message": "Solar Backend API is running ✅"})