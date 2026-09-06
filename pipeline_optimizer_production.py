import os
import pandas as pd
import pulp
import plotly.express as px

def run_optimization(num_lineups=20):
    print("[4/5] Generating GPP portfolio with 10:1 platform rules...")
    
    input_file = "vegas_adjusted_slate.csv"
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} not found. Ensure previous pipeline steps ran successfully.")
        
    df = pd.read_csv(input_file)
    
    # 1. STANDARDIZE COLUMNS
    df.columns = df.columns.str.strip().str.lower()
    
    col_map = {}
    for col in df.columns:
        if col in ['player', 'name', 'striker', 'batter', 'bowler']: col_map[col] = 'player_name'
        if col in ['proj_pts', 'points', 'projection']: col_map[col] = 'vegas_proj'
        if col in ['batting_team', 'squad', 'country']: col_map[col] = 'team'
    df.rename(columns=col_map, inplace=True)
    
    # 2. BULLETPROOF FALLBACKS
    if 'player_name' not in df.columns:
        df['player_name'] = ["Player_" + str(i) for i in df.index]

    if 'vegas_proj' not in df.columns:
        df['vegas_proj'] = df['base_proj'] if 'base_proj' in df.columns else 10.0
            
    if 'team' not in df.columns:
        print("⚠️ Warning: 'team' column missing! Assigning placeholder teams.")
        df['team'] = ['Team_A' if i % 2 == 0 else 'Team_B' for i in range(len(df))]
        
    if 'salary' not in df.columns: 
        df['salary'] = 8.5 
    
    if 'role' not in df.columns: 
        df['role'] = 'BAT'
    else:
        df['role'] = df['role'].astype(str).str.strip().str.upper()

    teams = df['team'].unique()
    team_A = teams[0]
    team_B = teams[1] if len(teams) > 1 else teams[0]
    available_roles = df['role'].unique()

    all_lineups = []
    print(f"Loading market and weather adjusted projections from: {input_file}\n")
    
    # 3. MILP LOOP
    for lineup_num in range(1, num_lineups + 1):
        prob = pulp.LpProblem(f"Cricket_DFS_10_1_Lineup_{lineup_num}", pulp.LpMaximize)
        player_vars = pulp.LpVariable.dicts("player", df.index, cat='Binary')
        
        # Maximize projections
        prob += pulp.lpSum([df.loc[i, 'vegas_proj'] * player_vars[i] for i in df.index])
        
        # Exactly 11 players
        prob += pulp.lpSum([player_vars[i] for i in df.index]) == 11
        
        # Salary Cap
        prob += pulp.lpSum([df.loc[i, 'salary'] * player_vars[i] for i in df.index]) <= 100.0
        
        # 10:1 PLATFORM RULES
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'team'] == team_A]) <= 10
        prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'team'] == team_B]) <= 10
        
        # DYNAMIC ROLE LIMITS (Only enforce if the role exists in the data)
        if 'WK' in available_roles:
            prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'WK']) >= 1
            prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'WK']) <= 4
            
        if 'BAT' in available_roles:
            prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) >= 1
            prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) <= 8
            
        if 'AR' in available_roles:
            prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'AR']) >= 1
            prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'AR']) <= 8
            
        if 'BOWL' in available_roles:
            prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) >= 1
            prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) <= 8
        
        # Overlap penalty (Diversity constraint)
        for prev_lineup in all_lineups:
            prob += pulp.lpSum([player_vars[i] for i in prev_lineup]) <= 9
            
        prob.solve(pulp.PULP_CBC_CMD(msg=False))
        
        if pulp.LpStatus[prob.status] != 'Optimal':
            print(f"Lineup {lineup_num} could not find an optimal solution. Stopping.")
            break
            
        selected_indices = [i for i in df.index if player_vars[i].varValue == 1]
        all_lineups.append(selected_indices)
        
        roster = df.loc[selected_indices].sort_values(by='vegas_proj', ascending=False)
        captain = roster.iloc[0]['player_name']
        vc = roster.iloc[1]['player_name']
        
        total_proj = roster['vegas_proj'].sum() + roster.iloc[0]['vegas_proj'] + (roster.iloc[1]['vegas_proj'] * 0.5)
        total_salary = roster['salary'].sum()
        
        print(f"Lineup {lineup_num:02d} | Proj: {total_proj:.2f} | Salary: {total_salary:.1f}/100 | (C): {captain} | (VC): {vc}")
        
    print(f"\nPortfolio Complete: {len(all_lineups)} fully compounded lineups exported.")
    
    # 4. SAVE ARTIFACTS
    if not all_lineups:
        print("❌ No lineups generated. Skipping HTML and CSV export.")
        return

    portfolio_rows = []
    for idx, lineup_indices in enumerate(all_lineups):
        for p_idx in lineup_indices:
            row = df.loc[p_idx].to_dict()
            row['lineup_id'] = idx + 1
            portfolio_rows.append(row)
            
    out_df = pd.DataFrame(portfolio_rows)
    out_df.to_csv("fully_compounded_gpp_portfolio.csv", index=False)
    
    print("[5/5] Generating interactive HTML risk dashboard...")
    try:
        exposure = out_df.groupby('player_name').size().reset_index(name='lineup_count')
        exposure['exposure_pct'] = (exposure['lineup_count'] / len(all_lineups)) * 100
        exposure = exposure.sort_values(by='exposure_pct', ascending=True)
        
        fig = px.bar(exposure, x='exposure_pct', y='player_name', orientation='h', 
                     title='10:1 GPP Portfolio Player Exposure (%)',
                     labels={'exposure_pct': 'Exposure (%)', 'player_name': 'Player'},
                     color='exposure_pct', color_continuous_scale='Viridis')
        
        fig.write_html("portfolio_report.html")
        print("Success! Open 'portfolio_report.html' in your browser.")
    except Exception as e:
        print(f"Warning: Could not generate HTML dashboard. {e}")

if __name__ == "__main__":
    run_optimization()
