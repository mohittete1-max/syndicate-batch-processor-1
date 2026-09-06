def calculate_dew_risk(temperature_c, humidity_pct, is_night_game):
    """Estimates dew severity score to modify second-innings bowling efficiency."""
    if not is_night_game:
        return 0.0
    dew_score = (humidity_pct / 100.0) * (temperature_c / 25.0)
    return round(min(max(dew_score, 0.0), 1.0), 2)
