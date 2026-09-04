import pandas as pd
import numpy as np

def generate_empirical_features(df_players, match_name="", market_odds=None, venue_data=None, weather_data=None):
    merged = df_players.copy()
    market_odds = market_odds or {}
    venue_data = venue_data or {'pitch_type': 'neutral', 'chase_bias': False}
    weather_data = weather_data or {'rain_prob': 0.0}
    
    is_womens = "women" in match_name.lower()
    rain_shortened = weather_data.get('rain_prob', 0.0) > 0.50
    pitch = venue_data.get('pitch_type', 'neutral')
    
    merged['market_win_prob'] = 0.50
    merged['implied_team_runs'] = 140.0 if is_womens else 175.0
    merged['proj_ownership'] = 30.0 
    
    for idx, row in merged.iterrows():
        team = row['team']
        role = row['role']
        if team in market_odds:
            merged.loc[idx, 'market_win_prob'] = market_odds[team].get('win_prob', 0.50)
            merged.loc[idx, 'implied_team_runs'] = market_odds[team].get('implied_runs', 140.0 if is_womens else 175.0)
            
        win_prob = merged.loc[idx, 'market_win_prob']
        
        # FULLY AUTONOMOUS OWNERSHIP DERIVATION:
        # Letting the engine weigh market probability and role organically without hardcoded tier bias.
        raw_popularity = (win_prob * 50.0) + (0.1 if role in ['AR', 'WK'] else 0.0)
        merged.loc[idx, 'proj_ownership'] = min(max(raw_popularity * 100.0, 5.0), 95.0)

    # Format-specific baselines
    if is_womens:
        merged['rolling_avg_pts'] = merged['role'].map({'WK': 45.0, 'AR': 52.0, 'BAT': 38.0, 'BOWL': 40.0}).fillna(38.0)
        merged['strike_rate'] = 105.0 * merged['market_win_prob']
        merged['economy_rate'] = 6.0 / merged['market_win_prob'].clip(lower=0.1)
    else:
        merged['rolling_avg_pts'] = merged['role'].map({'WK': 55.0, 'AR': 65.0, 'BAT': 48.0, 'BOWL': 50.0}).fillna(45.0)
        merged['strike_rate'] = 135.0 * merged['market_win_prob']
        merged['economy_rate'] = 8.5 / merged['market_win_prob'].clip(lower=0.1)

    # Weather Interruption Logic
    if rain_shortened:
        merged['rolling_avg_pts'] = merged.apply(lambda x: x['rolling_avg_pts'] * 1.15 if x['role'] in ['BAT', 'WK', 'BOWL'] else x['rolling_avg_pts'] * 0.85, axis=1)

    # Venue Micro-Targeting
    if pitch == 'batting':
        merged['rolling_avg_pts'] = merged.apply(lambda x: x['rolling_avg_pts'] * 1.12 if x['role'] in ['BAT', 'WK'] else x['rolling_avg_pts'] * 0.90, axis=1)
    elif pitch == 'bowling':
        merged['rolling_avg_pts'] = merged.apply(lambda x: x['rolling_avg_pts'] * 1.15 if x['role'] in ['BOWL', 'AR'] else x['rolling_avg_pts'] * 0.85, axis=1)

    merged['venue_avg_pts'] = merged['rolling_avg_pts'] * (merged['implied_team_runs'] / (130.0 if is_womens else 165.0))
    merged['opposition_factor'] = 1.10
    
    return merged
