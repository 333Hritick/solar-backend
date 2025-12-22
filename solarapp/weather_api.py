import requests
import os

API_KEY = os.getenv("WEATHER_API_KEY")

def get_forecast(city="Dehradun"):
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"q={city}&appid={API_KEY}&units=metric"
    )

    response = requests.get(url).json()

    next_day = response["list"][8]  # forecast approx for next day

    return {
        "temp": next_day["main"]["temp"],
        "humidity": next_day["main"]["humidity"],
        "clouds": next_day["clouds"]["all"],
        "sunlight": 100 - next_day["clouds"]["all"],
    }
