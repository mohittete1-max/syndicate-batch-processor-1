import pandas as pd
import pulp

def find_optimal_xi(match_id, input_csv="player_match_scores.csv"):
    print(f"Loading historical data and analyzing match: {match_id}...\n")
    df = pd.read_csv(input_csv)
    
    # Filter for the specific match
    match_df = df[df['match_id'] == match_id].copy()
    
    if match_df.empty:
        print(f"No data found for match {match_id}")
        return
        
    # 1. Define the Linear Programming problem
    prob = pulp.LpProblem("Optimal_DFS_Lineup", pulp.LpMaximize)
    
    # 2. Decision Variables: 0 or 1 (Include player or not)
    player_vars = pulp.LpVariable.dicts("Player", match_df.index, cat='Binary')
    
    # 3. Objective Function: Maximize total fantasy points
    prob += pulp.lpSum([match_df.loc[i, 'total_fantasy_pts'] * player_vars[i] for i in match_df.index]), "Total_Points"
    
    # 4. Core Constraint: Exactly 11 players
    prob += pulp.lpSum([player_vars[i] for i in match_df.index]) == 11, "11_Players"
    
    # Note: When we connect live data, we will add Salary, Role, and Team limits here!
    
    # 5. Solve the engine
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    # Extract the optimal lineup
    optimal_indices = [i for i in match_df.index if player_vars[i].varValue == 1]
    optimal_lineup = match_df.loc[optimal_indices].sort_values(by='total_fantasy_pts', ascending=False)
    
    print(f"=== THE PERFECT XI ===")
    print(f"Total Optimal Points: {pulp.value(prob.objective):.2f}\n")
    print(optimal_lineup[['player', 'runs', 'wickets', 'total_fantasy_pts']].to_string(index=False))

if __name__ == "__main__":
    # Dynamically grab the first valid match ID from our dataset to test the engine
    sample_df = pd.read_csv("player_match_scores.csv", nrows=1)
    if not sample_df.empty:
        test_match = sample_df['match_id'].iloc[0]
        find_optimal_xi(test_match)
