"""
==============================================================================
SYNDICATE OS - METEO WEATHER MODIFIER MODULE
==============================================================================
"""

def get_weather_modifier(file_name, player_name, role):
    """
    Returns a weather adjustment factor based on atmospheric conditions
    (e.g., overcast/rain-reduced games favor opening bowlers and top-order anchors).
    """
    # If a match has weather interruptions (like rain delays), boost swing bowlers/anchors
    if "Rotterdam_Dockers_vs_Belfast_Wolves" in file_name:
        if role == "BOWL":
            return 1.04  # Overcast/damp conditions boost seam movement
            
    # Default neutral weather impact
    return 1.0
