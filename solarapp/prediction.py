def simple_predict(production, sunlight):
    sunlight_factor = sunlight / 100
    prediction = production * (0.7 + sunlight_factor * 0.3)
    return round(prediction, 2)
