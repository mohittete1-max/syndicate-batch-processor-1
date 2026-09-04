# global_venue.py

def get_pitch_condition(venue_name):
    pitch_mapping = {
        "Arun Jaitley Stadium": "Batting-Paradise",
        "JSCA International Stadium Complex": "Spin-Friendly",
        "Wankhede Stadium": "Batting-Paradise",
        "Galle International Stadium": "Spin-Friendly",
        "Lord's Cricket Ground": "Seam-Friendly"
    }
    return pitch_mapping.get(venue_name, "Batting-Paradise")
