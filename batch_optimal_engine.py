import pandas as pd
import pulp
import time

def run_historical_batch(input_csv="player_match_scores.csv", output_csv="historical_perfect_lineups.csv"):
    print("Loading 142k player performances...")
    df = pd.read_csv(input_csv)
    
    match_ids = df['match_id'].unique()
    total_matches = len(match_ids)
    print(f"Found {total_matches} unique matches. Firing up the MILP batch engine...\n")
    
    master_results = []
    start_time = time.time()
    
    for idx, match_id in enumerate(match_ids, 1):
        match_df = df[df['match_id'] == match_id].copy()
        
        # Skip weird data anomalies with fewer than 11 players total
        if len(match_df) < 11:
            continue
            
        prob = pulp.LpProblem(f"Match_{match_id}", pulp.LpMaximize)
        player_vars = pulp.LpVariable.dicts("Player", match_df.index, cat='Binary')
        
        prob += pulp.lpSum([match_df.loc[i, 'total_fantasy_pts'] * player_vars[i] for i in match_df.index])
        prob += pulp.lpSum([player_vars[i] for i in match_df.index]) == 11
        
        # Suppress output logs to keep the loop fast
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        
        # Extract optimal players
        optimal_indices = [i for i in match_df.index if player_vars[i].varValue == 1]
        optimal_points = pulp.value(prob.objective)
        
        master_results.append({
            "match_id": match_id,
            "date": match_df['date'].iloc[0],
            "optimal_points": optimal_points,
            "optimal_roster": ", ".join(match_df.loc[optimal_indices, 'player'].tolist())
        })
        
        if idx % 500 == 0:
            print(f"Processed {idx}/{total_matches} matches...")
            
    # Export the ledger
    results_df = pd.DataFrame(master_results)
    # Sort by highest scoring matches of all time
    results_df = results_df.sort_values(by='optimal_points', ascending=False)
    results_df.to_csv(output_csv, index=False)
    
    elapsed = time.time() - start_time
    print(f"\nSuccess! Solved {len(results_df)} perfect lineups in {elapsed:.1f} seconds.")
    print(f"Saved to {output_csv}. You now hold the ultimate backtesting ledger.")

if __name__ == "__main__":
    run_historical_batch()
