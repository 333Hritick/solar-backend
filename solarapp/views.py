from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import QuoteRequest
from .serializers import QuoteRequestSerializer
import requests
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

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



@api_view(['POST'])
def calculate_emi(request):
    data = request.data
    cost = float(data.get('cost', 0))
    subsidy_percent = float(data.get('subsidy_percent', 0))
    down_payment = float(data.get('down_payment', 0))
    interest_rate = float(data.get('interest_rate', 0))
    tenure_years = int(data.get('tenure_years', 0))

    # Subsidy calculation
    subsidy_amount = (subsidy_percent / 100) * cost
    net_cost = cost - subsidy_amount - down_payment

    # EMI calculation
    R = (interest_rate / 12) / 100
    N = tenure_years * 12
    EMI = (net_cost * R * (1 + R)**N) / ((1 + R)**N - 1) if R > 0 else net_cost / N
    total_payment = EMI * N
    total_interest = total_payment - net_cost

    return Response({
        "original_cost": cost,
        "subsidy_amount": round(subsidy_amount, 2),
        "net_cost_after_subsidy": round(net_cost, 2),
        "emi_per_month": round(EMI, 2),
        "total_interest": round(total_interest, 2),
        "total_payment": round(total_payment, 2)
    })
    
    # login and register
@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()
    return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        return Response({'message': 'Login successful', 'username': username}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)