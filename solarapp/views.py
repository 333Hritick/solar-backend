from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth import get_user_model
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
import os,uuid
from .models import Device, ProductionData
from django.db import IntegrityError


TELEGRAM_BOT_TOKEN = "8084652463:AAGUVvnvNoNMQmEocqpROaFKqgHgP-C86ho"
TELEGRAM_CHAT_ID = "5698737028"


User = get_user_model()


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
        username=email,  # still required by AbstractUser
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    devices = Device.objects.filter(user=user)

    data = {
        "name": user.first_name,
        "email": user.email,
        "phone": profile.phone,
        "address": profile.address,
        "accounttype": profile.accounttype,
        "devices": [
            {
                "id": d.id,
                "name": d.name,
                "status": d.status,
                "token": d.token,
                "serial_number": d.serial_number,
                "location": d.location,
                "capacity_kw": d.capacity_kw,
                "installation_date": d.installation_date,
                "manufacturer": d.manufacturer,
                "description": d.description,
            }
            for d in devices
        ]
    }
    return Response(data)



API_KEY = os.getenv("WEATHER_API_KEY")

def get_forecast(city="Dehradun"):
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"q={city}&appid={API_KEY}&units=metric"
    )
    try:
        response = requests.get(url).json()

        # Defensive checks
        if "list" not in response or len(response["list"]) < 9:
            return {"temp": 25, "humidity": 50, "clouds": 20, "sunlight": 80}

        next_day = response["list"][8]  # ~24h later
        return {
            "temp": next_day["main"]["temp"],
            "humidity": next_day["main"]["humidity"],
            "clouds": next_day["clouds"]["all"],
            "sunlight": 100 - next_day["clouds"]["all"],
        }
    except Exception as e:
        print("Weather API error:", e)
        return {"temp": 25, "humidity": 50, "clouds": 20, "sunlight": 80}

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_device(request):
    """Generate random token for user’s device"""
    token = uuid.uuid4().hex
    device = Device.objects.create(
        user=request.user,
        name=request.data.get("name", "My Inverter"),
        token=token
    )
    return Response({"device_id": device.id, "token": device.token})

@api_view(["POST"])
def post_production(request):
    """ESP32 or simulator posts production data with token"""
    token = request.data.get("token")
    production = request.data.get("production")
    try:
        device = Device.objects.get(token=token)
        ProductionData.objects.create(device=device, production=production)
        return Response({"status": "ok", "production": production})
    except Device.DoesNotExist:
        return Response({"error": "Invalid device token"}, status=400)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mydata(request):
    """Return production history for logged-in user"""
    devices = Device.objects.filter(user=request.user)
    data = ProductionData.objects.filter(device__in=devices).order_by("-timestamp")[:20]
    return Response([{"production": d.production, "timestamp": d.timestamp} for d in data])






@api_view(["GET"])
def energypredict(request):
    # Simulate today’s production
    today_prod = round(random.uniform(40, 50), 1)
    consumption = round(today_prod * 0.7, 1)
    surplus = round(today_prod - consumption, 1)

    # Get tomorrow’s forecast
    weather = get_forecast("Dehradun")
    sunlight = weather.get("sunlight", 50)

    # Simple prediction formula
    predicted_next_day = round(today_prod * (0.7 + sunlight/100 * 0.3), 1)

    return Response({
        "today_production": today_prod,
        "consumption": consumption,
        "surplus": surplus,
        "credits": round(predicted_next_day * 10, 1),
        "weather": weather,
        "predicted_next_day": predicted_next_day
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





@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_device(request):
    try:
        token = uuid.uuid4().hex
        device = Device.objects.create(
            user=request.user,
            name=request.data.get("name", f"{request.user.first_name}'s Inverter"),
            token=token,
            serial_number=request.data.get("serial_number"),
            location=request.data.get("location"),
            capacity_kw=request.data.get("capacity_kw") or None,
            installation_date=request.data.get("installation_date") or None,
            manufacturer=request.data.get("manufacturer"),
            description=request.data.get("description")
        )
        return Response({"message": "Device registered successfully", "device_id": device.id})
    except IntegrityError:
        return Response({"error": "Serial number already registered"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)