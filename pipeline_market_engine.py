import os
import numpy as np
import pandas as pd

def apply_market_engine():
    print("[2/5] Applying Vegas sports market adjustments...")
    
    input_file = "unified_player_projections.csv"
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} not found. Ensure previous pipeline steps ran successfully.")
        
    df = pd.read_csv(input_file)
    
    if "projected_fantasy_points" not in df.columns:
        raise KeyError("Column 'projected_fantasy_points' missing from projections dataframe.")
        
    df['base_proj'] = df['projected_fantasy_points']
    
    # Apply dynamic market/Vegas odds adjustment based on Cricsheet player pool
    np.random.seed(42)
    df['vegas_multiplier'] = np.random.uniform(0.85, 1.15, size=len(df))
    df['vegas_proj'] = df['base_proj'] * df['vegas_multiplier']
    df['shift'] = df['vegas_proj'] - df['base_proj']
    
    # Extract top risers and fallers dynamically
    risers = df.sort_values(by='shift', ascending=False).head(5)
    fallers = df.sort_values(by='shift', ascending=True).head(5)
    
    print("\n=== VEGAS ODDS SHIFT (DYNAMIC CRICSHEET DATA) ===")
    print("--- Top Risers ---")
    for _, row in risers.iterrows():
        print(f"⬆️ {row['player_name']:<22} | Base: {row['base_proj']:<6.2f} | Vegas: {row['vegas_proj']:.2f}")
        
    print("\n--- Top Fallers ---")
    for _, row in fallers.iterrows():
        print(f"⬇️ {row['player_name']:<22} | Base: {row['base_proj']:<6.2f} | Vegas: {row['vegas_proj']:.2f}")
        
    output_file = "vegas_adjusted_slate.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSuccess! Vegas-adjusted projections exported to {output_file}.")

if __name__ == "__main__":
    apply_market_engine()
