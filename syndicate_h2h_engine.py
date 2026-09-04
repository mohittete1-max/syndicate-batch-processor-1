"""
==============================================================================
SYNDICATE OS - H2H HISTORICAL WEIGHTED ENGINE
Modular template for upcoming fixtures
==============================================================================
"""

import os
import json
import pandas as pd

def apply_h2h_historical_weights(df, h2h_history_dict):
    """
    Adjusts base projections using historical head-to-head performance 
    against the specific opposition team.
    """
    for idx, row in df.iterrows():
        player_name = row["Player"]
        if player_name in h2h_history_dict:
            h2h_multiplier = h2h_history_dict[player_name] # e.g., 1.15 for historical dominance
            df.loc[idx, "Base_Projection"] = round(row["Base_Projection"] * h2h_multiplier, 2)
            
    return df
