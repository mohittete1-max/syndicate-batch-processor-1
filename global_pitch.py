"""
==============================================================================
SYNDICATE OS - GLOBAL PITCH MODIFIER MODULE
==============================================================================
"""

def get_pitch_modifier(file_name, player_name, role, team):
    """
    Returns a multiplier (e.g., 1.05 for a boost, 0.95 for a penalty)
    based on venue conditions and player roles.
    """
    # Example venue-specific logic mapped from active fixtures
    if "South_Africa_vs_Zimbabwe" in file_name:
        # Pace-friendly tracks favor high-end fast bowlers
        if role == "BOWL":
            return 1.05
    elif "Sri_Lanka_Women_vs_UAE_Women" in file_name:
        # Spin/subcontinental slow tracks favor all-rounders and slow bowlers
        if role in ["ALL", "BOWL"]:
            return 1.03
            
    # Default neutral modifier
    return 1.0
