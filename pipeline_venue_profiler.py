VENUE_PROFILE_TEMPLATE = {
    "venue_name": "Standard Venue",
    "pitch_type": "balanced",
    "avg_first_innings_score": 160.0,
    "pace_wicket_share": 0.60,
    "spin_wicket_share": 0.40,
    "boundary_size_factor": 1.0,
    "chasing_bias_score": 1.0
}

VENUE_PROFILES = {
    "wankhede stadium": {
        "venue_name": "Wankhede Stadium, Mumbai",
        "pitch_type": "red_soil",
        "avg_first_innings_score": 172.5,
        "pace_wicket_share": 0.64,
        "spin_wicket_share": 0.36,
        "boundary_size_factor": 0.92,
        "chasing_bias_score": 1.15
    },
    "m. chinnaswamy stadium": {
        "venue_name": "M. Chinnaswamy Stadium, Bengaluru",
        "pitch_type": "black_soil",
        "avg_first_innings_score": 178.0,
        "pace_wicket_share": 0.58,
        "spin_wicket_share": 0.42,
        "boundary_size_factor": 0.88,
        "chasing_bias_score": 1.20
    }
}

def get_venue_profile(venue_name):
    """Normalizes venue strings and returns matching profile metrics or standard template."""
    if not venue_name:
        return VENUE_PROFILE_TEMPLATE
    
    normalized_input = str(venue_name).lower().strip()
    
    for key, profile in VENUE_PROFILES.items():
        if key in normalized_input:
            return profile
            
    return VENUE_PROFILE_TEMPLATE
