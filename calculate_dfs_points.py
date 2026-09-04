import pandas as pd

def build_fantasy_scores(input_csv="master_deliveries.csv", output_csv="player_match_scores.csv"):
    print("Loading 1.58 million deliveries into memory. This will take a few seconds...")
    df = pd.read_csv(input_csv)
    
    # --- BATTING METRICS ---
    print("Crunching batting metrics...")
    batting = df.groupby(['match_id', 'date', 'batter']).agg(
        runs=('batter_runs', 'sum'),
        balls_faced=('batter', 'count'),
        fours=('batter_runs', lambda x: (x == 4).sum()),
        sixes=('batter_runs', lambda x: (x == 6).sum())
    ).reset_index()
    
    # Base Points
    batting['bat_points'] = batting['runs'] + batting['fours'] + (batting['sixes'] * 2)
    
    # Milestone Bonuses
    batting['bat_points'] += batting['runs'].apply(
        lambda x: 4 if 30 <= x < 50 else (8 if 50 <= x < 100 else (16 if x >= 100 else 0))
    )
    
    # Strike Rate Points (standard T20 rules: min 10 balls)
    def calc_sr_points(row):
        if row['balls_faced'] >= 10:
            sr = (row['runs'] / row['balls_faced']) * 100
            if sr > 170: return 6
            elif sr > 150: return 4
            elif sr > 130: return 2
            elif sr < 50: return -6
            elif sr < 60: return -4
            elif sr <= 70: return -2
        return 0
        
    batting['sr_points'] = batting.apply(calc_sr_points, axis=1)
    batting['total_batting_pts'] = batting['bat_points'] + batting['sr_points']
    
    # --- BOWLING METRICS ---
    print("Crunching bowling metrics...")
    # Drop rows without a bowler
    bowling_df = df.dropna(subset=['bowler'])
    bowling = bowling_df.groupby(['match_id', 'date', 'bowler']).agg(
        wickets=('is_wicket', 'sum'),
        balls_bowled=('bowler', 'count')
    ).reset_index()
    
    # Base Points (25 per wicket)
    bowling['bowl_points'] = bowling['wickets'] * 25
    
    # Milestone Bonuses
    bowling['bowl_points'] += bowling['wickets'].apply(
        lambda x: 4 if x == 3 else (8 if x == 4 else (16 if x >= 5 else 0))
    )
    
    # Rename columns so we can merge cleanly on "player"
    batting = batting.rename(columns={'batter': 'player'})
    bowling = bowling.rename(columns={'bowler': 'player'})
    
    # --- MASTER MERGE ---
    print("Fusing profiles and generating final DFS scores...")
    master = pd.merge(batting, bowling, on=['match_id', 'date', 'player'], how='outer').fillna(0)
    master['total_fantasy_pts'] = master['total_batting_pts'] + master['bowl_points']
    
    # Sort by date (newest first), then by points
    master = master.sort_values(by=['date', 'total_fantasy_pts'], ascending=[False, False])
    
    # Export
    master.to_csv(output_csv, index=False)
    print(f"Success! Exported DFS points for {len(master)} player performances to {output_csv}.")

if __name__ == "__main__":
    build_fantasy_scores()
