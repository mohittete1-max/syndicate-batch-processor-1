import pandas as pd
import pulp

def optimize_advanced_slate(slate_csv="live_slate.csv"):
    print("Loading live slate and initializing Advanced MILP Engine...")
    try:
        df = pd.read_csv(slate_csv)
    except FileNotFoundError:
        print(f"Error: {slate_csv} missing.")
        return
        
    prob = pulp.LpProblem("Advanced_DFS_Lineup", pulp.LpMaximize)
    
    # 1. Decision Variables (Now 3 variables per player!)
    player_vars = pulp.LpVariable.dicts("Player", df.index, cat='Binary')
    captain_vars = pulp.LpVariable.dicts("Captain", df.index, cat='Binary')
    vc_vars = pulp.LpVariable.dicts("ViceCaptain", df.index, cat='Binary')
    
    # 2. Objective Function: Base Points + (1.0 * C_Points) + (0.5 * VC_Points)
    # (Because the base player_var already adds 1x, adding 1x for C makes it 2x total, and 0.5x for VC makes it 1.5x total)
    prob += pulp.lpSum([
        (df.loc[i, 'projected_points'] * player_vars[i]) + 
        (df.loc[i, 'projected_points'] * 1.0 * captain_vars[i]) + 
        (df.loc[i, 'projected_points'] * 0.5 * vc_vars[i]) 
        for i in df.index
    ]), "Total_Projected_Points"
    
    # 3. Core Lineup Constraints
    prob += pulp.lpSum([player_vars[i] for i in df.index]) == 11, "11_Players"
    prob += pulp.lpSum([df.loc[i, 'salary'] * player_vars[i] for i in df.index]) <= 100.0, "Salary_Cap"
    
    # 4. Multiplier Logic Constraints
    prob += pulp.lpSum([captain_vars[i] for i in df.index]) == 1, "Exactly_1_Captain"
    prob += pulp.lpSum([vc_vars[i] for i in df.index]) == 1, "Exactly_1_VC"
    
    for i in df.index:
        # A player MUST be in the lineup to be chosen as C or VC
        prob += captain_vars[i] <= player_vars[i], f"C_in_lineup_{i}"
        prob += vc_vars[i] <= player_vars[i], f"VC_in_lineup_{i}"
        # A player CANNOT be both Captain and Vice-Captain simultaneously
        prob += captain_vars[i] + vc_vars[i] <= 1, f"Not_both_{i}"
    
    # 5. DFS Role Limits
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'WK']) >= 1
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'WK']) <= 4
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) >= 3
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) <= 6
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'AR']) >= 1
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'AR']) <= 4
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) >= 3
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) <= 6
    
    # 6. Max 7 players per team
    teams = df['team'].unique()
    for team in teams:
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'team'] == team]) <= 7, f"Max_7_{team}"

    # Solve the Matrix
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    if pulp.LpStatus[prob.status] != 'Optimal':
        print("INFEASIBLE: Impossible to build a lineup with these constraints.")
        return
        
    print(f"\n=== ADVANCED OPTIMIZED LINEUP (WITH C & VC) ===")
    print(f"Total Projected Points: {pulp.value(prob.objective):.2f}")
    print(f"Total Salary Used: {sum(df.loc[i, 'salary'] * player_vars[i].varValue for i in df.index):.1f} / 100.0\n")
    
    print(f"{'Player':<20} | {'Team':<4} | {'Role':<4} | {'Salary':<6} | {'Tag':<4} | {'Points'}")
    print("-" * 65)
    
    for i in df.index:
        if player_vars[i].varValue == 1:
            tag = ""
            pts = df.loc[i, 'projected_points']
            if captain_vars[i].varValue == 1:
                tag = "(C)"
                pts *= 2.0
            elif vc_vars[i].varValue == 1:
                tag = "(VC)"
                pts *= 1.5
                
            print(f"{df.loc[i, 'player']:<20} | {df.loc[i, 'team']:<4} | {df.loc[i, 'role']:<4} | {df.loc[i, 'salary']:<6} | {tag:<4} | {pts:.1f}")

if __name__ == "__main__":
    optimize_advanced_slate()
