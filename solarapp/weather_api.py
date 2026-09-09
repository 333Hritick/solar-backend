import requests
import os

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

        next_day = response["list"][8]

        return {
            "temp": next_day["main"]["temp"],
            "humidity": next_day["main"]["humidity"],
            "clouds": next_day["clouds"]["all"],
            "sunlight": 100 - next_day["clouds"]["all"],
        }
    except Exception as e:
        print("Weather API error:", e)
        # Fallback values so frontend doesn’t break
        return {"temp": 25, "humidity": 50, "clouds": 20, "sunlight": 80}
