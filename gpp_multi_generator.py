import pandas as pd
import pulp

def generate_gpp_lineups(slate_csv="vegas_adjusted_slate.csv", num_lineups=20, max_overlap=8, output_csv="vegas_gpp_20_team_portfolio.csv"):
    print(f"Loading market-adjusted projections from: {slate_csv}")
    try:
        df = pd.read_csv(slate_csv)
    except FileNotFoundError:
        print(f"Error: '{slate_csv}' not found. Make sure you have run vegas_odds_integrator.py first.")
        return
        
    master_lineups = []
    previous_lineups = [] 
    
    print(f"Initializing MILP Engine: generating {num_lineups} unique lineups (Max Overlap: {max_overlap} players)...\n")
    
    for lineup_num in range(1, num_lineups + 1):
        prob = pulp.LpProblem(f"GPP_Lineup_{lineup_num}", pulp.LpMaximize)
        
        # 1. Decision Variables
        player_vars = pulp.LpVariable.dicts("Player", df.index, cat='Binary')
        captain_vars = pulp.LpVariable.dicts("Captain", df.index, cat='Binary')
        vc_vars = pulp.LpVariable.dicts("ViceCaptain", df.index, cat='Binary')
        
        # 2. Objective Function: Maximize Vegas-adjusted projected points
        prob += pulp.lpSum([
            (df.loc[i, 'projected_points'] * player_vars[i]) + 
            (df.loc[i, 'projected_points'] * 1.0 * captain_vars[i]) + 
            (df.loc[i, 'projected_points'] * 0.5 * vc_vars[i]) 
            for i in df.index
        ])
        
        # 3. Core Roster & Budget Constraints
        prob += pulp.lpSum([player_vars[i] for i in df.index]) == 11, "Total_11_Players"
        prob += pulp.lpSum([df.loc[i, 'salary'] * player_vars[i] for i in df.index]) <= 100.0, "Salary_Cap_100"
        
        # 4. Multiplier Constraints (1 C, 1 VC, must be in team, cannot be same player)
        prob += pulp.lpSum([captain_vars[i] for i in df.index]) == 1, "Exactly_1_Captain"
        prob += pulp.lpSum([vc_vars[i] for i in df.index]) == 1, "Exactly_1_VC"
        
        for i in df.index:
            prob += captain_vars[i] <= player_vars[i], f"C_in_team_{i}"
            prob += vc_vars[i] <= player_vars[i], f"VC_in_team_{i}"
            prob += captain_vars[i] + vc_vars[i] <= 1, f"Separate_C_VC_{i}"
        
        # 5. Standard DFS Role Constraints
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'WK']) >= 1
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'WK']) <= 4
        
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) >= 3
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) <= 6
        
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'AR']) >= 1
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'AR']) <= 4
        
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) >= 3
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) <= 6
        
        # 6. Team Representation Limit (Max 7 from one nation/franchise)
        teams = df['team'].unique()
        for team in teams:
            prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'team'] == team]) <= 7, f"Max_7_{team}"
            
        # 7. Portfolio Diversification (Overlap Limit against previous teams)
        for past_lineup in previous_lineups:
            prob += pulp.lpSum([player_vars[i] for i in past_lineup]) <= max_overlap

        # Solve without verbose solver output
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        
        if pulp.LpStatus[prob.status] != 'Optimal':
            print(f"Reached optimization limit at Lineup {lineup_num - 1}. No additional combinations satisfy constraints.")
            break
            
        selected_indices = [i for i in df.index if player_vars[i].varValue == 1]
        previous_lineups.append(selected_indices)
        
        # Extract Roster Metadata
        c_name = ""
        vc_name = ""
        roster_names = []
        for i in selected_indices:
            if captain_vars[i].varValue == 1:
                c_name = df.loc[i, 'player']
            elif vc_vars[i].varValue == 1:
                vc_name = df.loc[i, 'player']
            else:
                roster_names.append(df.loc[i, 'player'])
                
        total_salary_used = sum(df.loc[i, 'salary'] for i in selected_indices)
        proj_score = round(pulp.value(prob.objective), 2)
        
        lineup_data = {
            "Lineup_Num": lineup_num,
            "Projected_Pts": proj_score,
            "Salary_Used": round(total_salary_used, 1),
            "Captain": c_name,
            "Vice_Captain": vc_name
        }
        
        for idx, name in enumerate(roster_names, 1):
            lineup_data[f"Player_{idx}"] = name
            
        master_lineups.append(lineup_data)
        print(f"Lineup {lineup_num:02d} | Proj: {proj_score:6.2f} | Salary: {total_salary_used:4.1f}/100 | (C): {c_name:<16} | (VC): {vc_name}")

    # Export compiled portfolio
    if master_lineups:
        export_df = pd.DataFrame(master_lineups)
        export_df.to_csv(output_csv, index=False)
        print(f"\nPortfolio Complete: {len(export_df)} lineups exported to '{output_csv}'.")
    else:
        print("\nNo lineups generated.")

if __name__ == "__main__":
    generate_gpp_lineups(
        slate_csv="vegas_adjusted_slate.csv", 
        num_lineups=20, 
        max_overlap=8, 
        output_csv="vegas_gpp_20_team_portfolio.csv"
    )
