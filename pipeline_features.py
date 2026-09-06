import os
import pandas as pd

def extract_player_features(master_csv="master_cricket_dataset.csv"):
    """
    Aggregates ball-by-ball master data into player-level features for DFS optimization,
    safely adapting to whichever columns are present in the consolidated dataset.
    """
    if not os.path.exists(master_csv):
        print(f"Master dataset not found: {master_csv}")
        return None
        
    print("Loading master dataset for feature engineering...")
    df = pd.read_csv(master_csv, low_memory=False)
    
    # Dynamically detect available columns
    batter_col = 'striker' if 'striker' in df.columns else ('batter' if 'batter' in df.columns else None)
    runs_col = 'runs_off_bat' if 'runs_off_bat' in df.columns else ('runs_batter' if 'runs_batter' in df.columns else 'runs')
    total_runs_col = 'runs_total' if 'runs_total' in df.columns else runs_col
    
    if not batter_col:
        raise ValueError(f"Could not find striker/batter column. Available columns: {list(df.columns)[:15]}")
        
    print(f"Using batter column: '{batter_col}' and runs column: '{runs_col}'")
    
    # Build grouping keys dynamically based on available metadata columns
    batting_group_cols = [batter_col]
    if 'match_type' in df.columns:
        batting_group_cols.append('match_type')
    elif 'event' in df.columns:
        batting_group_cols.append('event')
        
    bowling_group_cols = ['bowler']
    if 'match_type' in df.columns:
        bowling_group_cols.append('match_type')
    elif 'event' in df.columns:
        bowling_group_cols.append('event')
    
    dismissal_col = 'player_dismissed' if 'player_dismissed' in df.columns else ('wicket_kind' if 'wicket_kind' in df.columns else None)
    
    print("Calculating batting metrics...")
    agg_dict_batting = {
        'total_runs': (runs_col, 'sum'),
        'balls_faced': (runs_col, 'count')
    }
    if dismissal_col:
        agg_dict_batting['dismissals'] = (dismissal_col, lambda x: (x.notna()).sum())
        
    batting = df.groupby(batting_group_cols).agg(**agg_dict_batting).reset_index()
    batting.rename(columns={batter_col: 'batter'}, inplace=True)
    batting['batting_strike_rate'] = (batting['total_runs'] / batting['balls_faced']) * 100
    
    print("Calculating bowling metrics...")
    agg_dict_bowling = {
        'runs_conceded': (total_runs_col, 'sum'),
        'balls_bowled': ('ball', 'count') if 'ball' in df.columns else (total_runs_col, 'count')
    }
    if dismissal_col:
        agg_dict_bowling['wickets_taken'] = (dismissal_col, lambda x: (x.notna()).sum())
        
    bowling = df.groupby(bowling_group_cols).agg(**agg_dict_bowling).reset_index()
    bowling['economy_rate'] = bowling['runs_conceded'] / (bowling['balls_bowled'] / 6)
    
    batting.to_csv("batter_features.csv", index=False)
    bowling.to_csv("bowler_features.csv", index=False)
    print("Player feature extraction complete! Saved batter_features.csv and bowler_features.csv.")

if __name__ == "__main__":
    extract_player_features()
