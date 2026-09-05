import pandas as pd
import pulp

def optimize_live_slate(slate_csv="live_slate.csv"):
    print("Loading live slate projections...")
    try:
        df = pd.read_csv(slate_csv)
    except FileNotFoundError:
        print(f"Error: Could not find {slate_csv}. Please create it first.")
        return
        
    prob = pulp.LpProblem("Live_DFS_Lineup", pulp.LpMaximize)
    player_vars = pulp.LpVariable.dicts("Player", df.index, cat='Binary')
    
    # Objective: Maximize Projected Points
    prob += pulp.lpSum([df.loc[i, 'projected_points'] * player_vars[i] for i in df.index]), "Total_Projected_Points"
    
    # Constraint 1: Exactly 11 Players
    prob += pulp.lpSum([player_vars[i] for i in df.index]) == 11, "11_Players"
    
    # Constraint 2: Salary Cap (Max 100 Credits)
    prob += pulp.lpSum([df.loc[i, 'salary'] * player_vars[i] for i in df.index]) <= 100.0, "Salary_Cap"
    
    # Constraint 3: DFS Role Limits
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'WK']) >= 1
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'WK']) <= 4
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) >= 3
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) <= 6
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'AR']) >= 1
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'AR']) <= 4
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) >= 3
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) <= 6
    
    # Constraint 4: Max 7 players per team
    teams = df['team'].unique()
    for team in teams:
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'team'] == team]) <= 7, f"Max_7_{team}"

    # Solve the Matrix
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    if pulp.LpStatus[prob.status] != 'Optimal':
        print("Status: INFEASIBLE - Impossible to build a valid lineup with this salary/projection setup.")
        return
        
    optimal_indices = [i for i in df.index if player_vars[i].varValue == 1]
    optimal_lineup = df.loc[optimal_indices].sort_values(by=['role', 'salary'], ascending=[False, False])
    
    total_salary = optimal_lineup['salary'].sum()
    total_proj = pulp.value(prob.objective)
    
    print(f"\n=== OPTIMIZED LIVE LINEUP ===")
    print(f"Total Projected Points: {total_proj:.2f}")
    print(f"Total Salary Used: {total_salary:.1f} / 100.0\n")
    print(optimal_lineup[['player', 'team', 'role', 'salary', 'projected_points']].to_string(index=False))

if __name__ == "__main__":
    optimize_live_slate()
