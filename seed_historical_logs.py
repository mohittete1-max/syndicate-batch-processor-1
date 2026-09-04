import pandas as pd
import numpy as np
import os

WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
FILE_PATH = os.path.join(WORKSPACE_DIR, "cricdata_historical_logs.csv")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

# Generate 500 rows of logically correlated dummy performance data for the ML to train on
np.random.seed(42)
n_rows = 500

data = {
    'rolling_avg_pts': np.random.uniform(25, 75, n_rows),
    'venue_avg_pts': np.random.uniform(30, 80, n_rows),
    'strike_rate': np.random.uniform(90, 160, n_rows),
    'economy_rate': np.random.uniform(4.5, 9.5, n_rows),
    'opposition_factor': np.random.uniform(0.8, 1.3, n_rows),
    'market_win_prob': np.random.uniform(0.2, 0.8, n_rows),
    'implied_team_runs': np.random.uniform(120, 190, n_rows),
}

df = pd.DataFrame(data)

# Create 'actual_fantasy_points' as a function of the features with some added noise (variance)
df['actual_fantasy_points'] = (
    (df['rolling_avg_pts'] * 0.4) + 
    (df['venue_avg_pts'] * 0.2) + 
    (df['strike_rate'] * 0.15) - 
    (df['economy_rate'] * 3) + 
    (df['market_win_prob'] * 20) + 
    (df['implied_team_runs'] * 0.1) * df['opposition_factor']
) + np.random.normal(0, 15, n_rows) # Adding realistic DFS variance

# Ensure no negative points are logged
df['actual_fantasy_points'] = df['actual_fantasy_points'].clip(lower=0).round(1)

df.to_csv(FILE_PATH, index=False)
print(f"✅ Generated {n_rows} rows of seeded historical training data at {FILE_PATH}")
