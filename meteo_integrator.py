import requests
import pandas as pd
import os

def fetch_venue_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,cloud_cover",
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        hourly = data.get("hourly", {})
        return {
            "temp": hourly.get("temperature_2m", [25])[0],
            "humidity": hourly.get("relative_humidity_2m", [50])[0],
            "wind": hourly.get("wind_speed_10m", [10])[0],
            "precip": hourly.get("precipitation", [0])[0],
            "cloud": hourly.get("cloud_cover", [20])[0]
        }
    except Exception as e:
        print(f"Weather fetch failed: {e}. Defaulting to neutral conditions.")
        return {"temp": 28, "humidity": 50, "wind": 12, "precip": 0, "cloud": 20}

def apply_weather_multipliers(input_file="vegas_adjusted_slate.csv", output_file="weather_and_vegas_adjusted_slate.csv", venue_coords=(28.6139, 77.2090)):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Run Vegas integrator first.")
        return

    print(f"Fetching live meteorological data from Open-Meteo API...")
    wx = fetch_venue_weather(venue_coords[0], venue_coords[1])
    print(f"Conditions -> Temp: {wx['temp']}°C | Humidity: {wx['humidity']}% | Wind: {wx['wind']} km/h | Cloud: {wx['cloud']}% | Rain Risk: {wx['precip']}mm")

    df = pd.read_csv(input_file)
    
    pace_multiplier = 1.0
    spin_multiplier = 1.0
    bat_multiplier = 1.0

    if wx["humidity"] > 70 and wx["cloud"] > 50:
        pace_multiplier = 1.08
        spin_multiplier = 0.94
        print("-> Atmospheric Profile: Heavy cloud & moisture. Boosting pace bowling ceiling; discounting spin control.")
    elif wx["humidity"] > 80:
        pace_multiplier = 1.03
        spin_multiplier = 0.90
        bat_multiplier = 1.04
        print("-> Atmospheric Profile: High dew factor detected. Heavily discounting spin bowlers; boosting batting control.")
    else:
        print("-> Atmospheric Profile: Neutral playing conditions.")

    adjusted_points = []
    for _, row in df.iterrows():
        # Compound directly on top of the existing Vegas-adjusted projection
        base_proj = row["projected_points"]
        role = row["role"]
        
        if role == "BOWL":
            factor = pace_multiplier
        elif role == "AR":
            factor = (pace_multiplier + bat_multiplier) / 2
        elif role in ["BAT", "WK"]:
            factor = bat_multiplier
        else:
            factor = 1.0

        if wx["precip"] > 1.0:
            factor *= 0.95

        adjusted_points.append(round(base_proj * factor, 2))

    df["projected_points"] = adjusted_points
    df.to_csv(output_file, index=False)
    print(f"Success! Fully compounded Vegas + Weather projections exported to {output_file}.")

if __name__ == "__main__":
    apply_weather_multipliers()
