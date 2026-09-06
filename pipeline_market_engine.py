import os
import pandas as pd
from pipeline_venue_profiler import get_venue_profile
from pipeline_weather_injector import calculate_dew_risk

def apply_market_and_environmental_adjustments(
    batting_csv="batter_features.csv", 
    bowling_csv="bowler_features.csv", 
    venue_name="Standard Venue", 
    temp_c=28.0, 
    humidity=75.0, 
    is_night=True, 
    implied_team_win_prob=0.55
):
    """
    Blends historical player metrics with venue profiles, dew/weather risk, 
    and betting market implied probabilities to generate unified player projections.
    """
    if not os.path.exists(batting_csv) or not os.path.exists(bowling_csv):
        print("Base feature CSVs missing.")
        return None
        
    batting = pd.read_csv(batting_csv)
    bowling = pd.read_csv(bowling_csv)
    
    # 1. Fetch Venue Profile Factors
    venue_profile = get_venue_profile(venue_name)
    boundary_factor = venue_profile['boundary_size_factor']
    
    # 2. Calculate Dew Risk
    dew_score = calculate_dew_risk(temp_c, humidity, is_night)
    
    # 3. Market Odds Scaling Factor
    market_multiplier = 0.8 + (implied_team_win_prob * 0.4)
    
    # Projections for Batting
    batting['batting_proj'] = (
        (batting['total_runs'] * 1.0 + (batting['batting_strike_rate'] > 130).astype(int) * 10)
        * (2.0 - boundary_factor)
        * market_multiplier
    )
    
    # Projections for Bowling
    dew_penalty = (1.0 - (dew_score * 0.15))
    bowling['bowling_proj'] = (
        (bowling['wickets_taken'] * 25.0 + (bowling['economy_rate'] < 7.5).astype(int) * 8)
        * dew_penalty
        * market_multiplier
    )
    
    # Merge on player name to create a unified master pool handling all-rounders properly
    batting.rename(columns={'batter': 'player_name'}, inplace=True)
    bowling.rename(columns={'bowler': 'player_name'}, inplace=True)
    
    unified_pool = pd.merge(
        batting[['player_name', 'batting_proj', 'total_runs', 'batting_strike_rate']], 
        bowling[['player_name', 'bowling_proj', 'wickets_taken', 'economy_rate']], 
        on='player_name', 
        how='outer'
    ).fillna(0)
    
    # Combined fantasy projection and intelligent role assignment
    unified_pool['projected_fantasy_points'] = unified_pool['batting_proj'] + unified_pool['bowling_proj']
    
    def assign_role(row):
        if row['batting_proj'] > 150 and row['bowling_proj'] > 150:
            return 'AR'
        elif row['bowling_proj'] > row['batting_proj']:
            return 'BOWL'
        else:
            return 'BAT'
            
    unified_pool['role'] = unified_pool.apply(assign_role, axis=1)
    unified_pool['credits'] = 8.5 # Baseline pricing
    
    unified_pool.to_csv("unified_player_projections.csv", index=False)
    print("Unified player projections with correct roles successfully compiled.")
    return unified_pool

if __name__ == "__main__":
    apply_market_and_environmental_adjustments()
