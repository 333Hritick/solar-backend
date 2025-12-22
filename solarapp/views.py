from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import QuoteRequest
from .models import Profile
from .serializers import QuoteRequestSerializer,EnergyOrderSerializer
import requests
import random
from .weather_api import get_forecast
from .prediction import simple_predict
from .models import EnergyOrder, EnergyToken
import threading



TELEGRAM_BOT_TOKEN = "8084652463:AAGUVvnvNoNMQmEocqpROaFKqgHgP-C86ho"
TELEGRAM_CHAT_ID = "5698737028"


def send_telegram_async(message: str):
    """Send telegram message in background thread"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram Error:", e)


@api_view(['POST'])
def create_quote(request):
    serializer = QuoteRequestSerializer(data=request.data)

    if serializer.is_valid():
        quote = serializer.save()

        message = (
            f"📩 New Quote Request!\n\n"
            f"👤 Name: {quote.name}\n"
            f"📧 Email: {quote.email}\n"
            f"📞 Phone: {quote.phone}\n"
            f"🏙️ District: {quote.district}\n"
            f"💵 Monthly Bill: {quote.monthlyBill}\n"
            f"🏠 Rooftop Area: {quote.rooftopArea}\n"
            f"💬 Message: {quote.message or 'N/A'}\n"
            f"🕒 Submitted at: {quote.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # 🚀 Send message in background (fast)
        threading.Thread(target=send_telegram_async, args=(message,)).start()

        # ⚡ Respond immediately (no waiting for Telegram)
        return Response(
            {"message": "Quote request submitted successfully!"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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

    subsidy_amount = (subsidy_percent / 100) * cost
    net_cost = cost - subsidy_amount - down_payment

    R = (interest_rate / 12) / 100
    N = tenure_years * 12

    EMI = (net_cost * R * (1 + R) ** N) / ((1 + R) ** N - 1) if R > 0 else net_cost / N
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



@api_view(['POST'])
def register_user(request):
    name = request.data.get('name')
    email = request.data.get('email')
    phone = request.data.get('phone')
    password = request.data.get('password')
    address = request.data.get('address')
    accounttype = request.data.get('accounttype')

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=400)

    
    user = User.objects.create_user(
        username=email,   
        email=email,
        password=password,
        first_name=name
    )

   
    profile = user.profile
    profile.phone = phone
    profile.address = address
    profile.accounttype = accounttype
    profile.save()

    return Response({"message": "User registered successfully"}, status=201)

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(username=email, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    return Response({
        'name': user.first_name,
        'email': user.email,
        'access': access_token,
        'refresh': str(refresh)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    data = {
        "name": user.first_name,
        "email": user.email,
        "phone": profile.phone,
        "address": profile.address,
        "accounttype": profile.accounttype
    }

    return Response(data)



@api_view(['GET'])
def next_day_energy(request):
    today_prod = round(random.uniform(40, 50), 1)
    weather = get_forecast("Dehradun")
    predicted = simple_predict(today_prod, weather["sunlight"])

    print("DEBUG WEATHER:", weather)


    return Response({
        "today_production": today_prod,
        "weather": weather,
        "predicted_next_day": predicted
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    amount = request.data.get("amount")
    price = request.data.get("price")
    order_type = request.data.get("order_type")

    order = EnergyOrder.objects.create(
        user=user,
        amount=amount,
        price=price,
        order_type=order_type,
        renewable_type="Solar"
    )

    return Response({"message": "Order created", "order_id": order.id})


@api_view(['GET'])
def get_offers(request):
    offers = EnergyOrder.objects.filter(is_active=True)
    serializer = EnergyOrderSerializer(offers, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_trade(request, order_id):
    try:
        order = EnergyOrder.objects.get(id=order_id)
        order.is_active = False
        order.save()
        return Response({"message": "Trade executed successfully"})
    except EnergyOrder.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)
