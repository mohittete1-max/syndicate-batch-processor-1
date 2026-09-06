import os
import pandas as pd
import pulp

def optimize_advanced_lineup(batter_csv="batter_features.csv", bowler_csv="bowler_features.csv", budget=100.0):
    if not os.path.exists(batter_csv) or not os.path.exists(bowler_csv):
        print("Feature CSVs not found.")
        return
        
    batters = pd.read_csv(batter_csv)
    bowlers = pd.read_csv(bowler_csv)
    
    # Generate mock projections and pricing for demonstration
    batters['fantasy_points'] = batters['total_runs'] * 1.0 + (batters['batting_strike_rate'] > 130).astype(int) * 10
    batters['credits'] = 8.5
    batters['role'] = 'BAT' # Can be refined if all-rounder data is split
    
    bowlers['fantasy_points'] = bowlers['wickets_taken'] * 25.0 + (bowlers['economy_rate'] < 7.5).astype(int) * 8
    bowlers['credits'] = 8.5
    bowlers['role'] = 'BOWL'

    # Combine into a single player pool dataframe for unified constraint handling
    players = pd.concat([batters, bowlers], ignore_index=True)
    
    prob = pulp.LpProblem("Advanced_Fantasy_Cricket", pulp.LpMaximize)
    
    # Decision variables: x[i] = 1 if player selected, c[i] = 1 if Captain, vc[i] = 1 if Vice-Captain
    x = {i: pulp.LpVariable(f"sel_{i}", cat='Binary') for i in players.index}
    c = {i: pulp.LpVariable(f"cap_{i}", cat='Binary') for i in players.index}
    vc = {i: pulp.LpVariable(f"vcap_{i}", cat='Binary') for i in players.index}
    
    # Objective: Maximize base points + extra weights for Captain (1x bonus) and VC (0.5x bonus)
    prob += pulp.lpSum(
        players.loc[i, 'fantasy_points'] * x[i] +
        players.loc[i, 'fantasy_points'] * c[i] * 1.0 +
        players.loc[i, 'fantasy_points'] * vc[i] * 0.5
        for i in players.index
    )
    
    # Budget constraint
    prob += pulp.lpSum(players.loc[i, 'credits'] * x[i] for i in players.index) <= budget
    
    # Squad size constraint (Exactly 11 players)
    prob += pulp.lpSum(x.values()) == 11
    
    # Exactly 1 Captain and 1 Vice-Captain must be chosen from the selected players
    prob += pulp.lpSum(c.values()) == 1
    prob += pulp.lpSum(vc.values()) == 1
    for i in players.index:
        prob += c[i] <= x[i]  # Captain must be in the selected 11
        prob += vc[i] <= x[i] # Vice-Captain must be in the selected 11
        prob += c[i] + vc[i] <= 1 # A player cannot be both C and VC
        
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    print(f"Advanced Optimization Status: {pulp.LpStatus[prob.status]}")
    
    print("\n--- Final Tournament Lineup ---")
    for i in players.index:
        if x[i].value() == 1:
            role_tag = " (C)" if c[i].value() == 1 else (" (VC)" if vc[i].value() == 1 else "")
            name = players.loc[i, 'batter'] if 'batter' in players.columns and pd.notna(players.loc[i, 'batter']) else players.loc[i, 'bowler']
            print(f"- {name}{role_tag} [{players.loc[i, 'role']}]")

if __name__ == "__main__":
    optimize_advanced_lineup()
