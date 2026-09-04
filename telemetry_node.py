# telemetry_node.py

def get_match_telemetry(match_name):
    """
    Simulates an environmental radar fetching live pitch and weather data.
    Returns the pitch type and the mathematical multipliers for the PuLP engine.
    """
    print(f"📡 Scanning environmental telemetry for: {match_name}...")
    
    # 4 Core Pitch Archetypes and their mathematical impact on player roles
    conditions = [
        {"type": "Dusty / Spin-Friendly", "multipliers": {"BAT": 0.9, "PACE": 0.8, "SPIN": 1.4, "AR": 1.1}},
        {"type": "Hard / Batting Paradise", "multipliers": {"BAT": 1.3, "PACE": 0.9, "SPIN": 0.8, "AR": 1.0}},
        {"type": "Green / Pacer's Wicket", "multipliers": {"BAT": 0.85, "PACE": 1.4, "SPIN": 0.9, "AR": 1.1}},
        {"type": "Balanced / Neutral Track", "multipliers": {"BAT": 1.0, "PACE": 1.0, "SPIN": 1.0, "AR": 1.0}}
    ]
    
    # Deterministically pick a condition based on the match name for consistency
    index = len(match_name) % len(conditions)
    active_condition = conditions[index]
    
    return active_condition

if __name__ == "__main__":
    # Test the radar
    test_data = get_match_telemetry("CSK vs MI")
    print(f"✅ Pitch Condition Locked: {test_data['type']}")
    print(f"✅ Math Multipliers: {test_data['multipliers']}")
