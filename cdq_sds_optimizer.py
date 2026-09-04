import os
import datetime
import math
import pandas as pd
import plotly.express as px
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD

# ==========================================
# 0. STABLE POISSON MATH CORE (WOMEN'S T20)
# ==========================================
def poisson_probability(k, lambd):
    return (math.exp(-lambd) * (lambd ** k)) / math.factorial(k)

def calculate_batting_ev(expected_runs):
    base_points = expected_runs 
    prob_duck = poisson_probability(0, expected_runs)
    prob_30_plus = 1 - sum(poisson_probability(k, expected_runs) for k in range(30))
    prob_50_plus = 1 - sum(poisson_probability(k, expected_runs) for k in range(50))
    return base_points + (-2 * prob_duck) + (4 * prob_30_plus) + (8 * prob_50_plus)

def calculate_bowling_ev(expected_wickets):
    base_points = expected_wickets * 25
    prob_3_plus = 1 - sum(poisson_probability(k, expected_wickets) for k in range(3))
    prob_4_plus = 1 - sum(poisson_probability(k, expected_wickets) for k in range(4))
    return base_points + (4 * prob_3_plus) + (8 * prob_4_plus)

def calculate_player_ev(df, toss_decision="bowl", venue_type="bowling"):
    print("   -> Running Poisson Core for CDQ-W vs SDS-W (Organic C/VC Solver)...")
    
    pitch_multipliers = {
        'batting': {'runs': 1.10, 'wickets': 0.90},
        'bowling': {'runs': 0.80, 'wickets': 1.25}, 
        'spin':    {'runs': 0.85, 'wickets': 1.20},
        'balanced':{'runs': 1.00, 'wickets': 1.00}
    }
    pitch_effect = pitch_multipliers.get(venue_type, pitch_multipliers['bowling'])
    toss_multiplier = 1.05 if toss_decision == "bowl" else 0.95

    team_a_name = df['team'].iloc[0] if not df.empty else "CDQ"
    vegas_implied_totals = {team_a_name: 115.5, 'default': 105.5}
    
    projected_points_list = []
    base_points_list = []
    
    for index, row in df.iterrows():
        role = row.get('role', 'bat')
        credits = float(row.get('credits', 8.5))
        team = row.get('team')
        
        team_total = vegas_implied_totals.get(team, vegas_implied_totals['default'])
        vegas_multiplier = (team_total / 110.0) * toss_multiplier
        
        credit_factor = credits / 8.5
        
        total_ev = 0
        if role in ['bat', 'wk']:
            lambda_runs = credit_factor * 16.0 * vegas_multiplier * pitch_effect['runs']
            total_ev = calculate_batting_ev(lambda_runs)
        elif role == 'bowl':
            lambda_wickets = credit_factor * 1.8 * pitch_effect['wickets']
            total_ev = calculate_bowling_ev(max(lambda_wickets, 0.1))
        elif role == 'ar':
            lambda_runs = credit_factor * 12.0 * vegas_multiplier * pitch_effect['runs']
            lambda_wickets = credit_factor * 1.2 * pitch_effect['wickets']
            total_ev = calculate_batting_ev(lambda_runs) + calculate_bowling_ev(max(lambda_wickets, 0.1))
            
        total_ev += 6.0 
        base_points_list.append(total_ev * 0.9)
        projected_points_list.append(total_ev)
        
    df['base_score'] = base_points_list
    df['projected_points'] = projected_points_list
    return df


# ==========================================
# 1. AUTHENTIC SQUAD POOL
# ==========================================
def get_clean_dataframe():
    print("-> Loading complete authentic CDQ-W vs SDS-W squad pool...")
    authentic_roster = [
        {"name": "S Sehrawat", "team": "SDS-W", "role": "bat", "credits": 8.0},
        {"name": "R Vishwa", "team": "SDS-W", "role": "ar", "credits": 8.0},
        {"name": "D Nagar", "team": "SDS-W", "role": "ar", "credits": 7.5},
        {"name": "T Singh", "team": "SDS-W", "role": "ar", "credits": 7.5},
        {"name": "N Singh", "team": "SDS-W", "role": "wk", "credits": 6.5},
        {"name": "T Singh (WK)", "team": "SDS-W", "role": "wk", "credits": 6.0},
        {"name": "H Chaudhary", "team": "SDS-W", "role": "ar", "credits": 7.5},
        {"name": "E Bhadana", "team": "SDS-W", "role": "bowl", "credits": 7.5},
        {"name": "G Baghel", "team": "SDS-W", "role": "bowl", "credits": 7.5},
        {"name": "P Punia", "team": "SDS-W", "role": "bat", "credits": 6.0},
        {"name": "A Pahuja", "team": "SDS-W", "role": "bat", "credits": 6.5},
        {"name": "A Kumari (AR)", "team": "SDS-W", "role": "ar", "credits": 6.5},
        {"name": "Kashish", "team": "SDS-W", "role": "ar", "credits": 6.0},
        {"name": "Harshita", "team": "SDS-W", "role": "bowl", "credits": 7.0},
        {"name": "A Kumari (Bowl)", "team": "SDS-W", "role": "bowl", "credits": 6.5},
        {"name": "M Singh", "team": "SDS-W", "role": "bowl", "credits": 6.0},
        {"name": "Yashika", "team": "SDS-W", "role": "bowl", "credits": 6.0},
        
        {"name": "D Sharma", "team": "CDQ", "role": "ar", "credits": 6.5},
        {"name": "Saachi", "team": "CDQ", "role": "ar", "credits": 6.5},
        {"name": "Monika", "team": "CDQ", "role": "bat", "credits": 7.5},
        {"name": "A Goel", "team": "CDQ", "role": "bat", "credits": 7.0},
        {"name": "M Bidhuri", "team": "CDQ", "role": "bat", "credits": 6.5},
        {"name": "Priyadarshini", "team": "CDQ", "role": "wk", "credits": 8.0},
        {"name": "N Tanwar", "team": "CDQ", "role": "wk", "credits": 8.0},
        {"name": "N Bhist", "team": "CDQ", "role": "bat", "credits": 8.0},
        {"name": "R Kondal", "team": "CDQ", "role": "bat", "credits": 7.5},
        {"name": "M Khatri", "team": "CDQ", "role": "bat", "credits": 7.5},
        {"name": "N Parmar", "team": "CDQ", "role": "ar", "credits": 8.0},
        {"name": "A Jain", "team": "CDQ", "role": "ar", "credits": 8.0},
        {"name": "T Chauhan", "team": "CDQ", "role": "ar", "credits": 7.0},
        {"name": "K Kumar", "team": "CDQ", "role": "ar", "credits": 6.5},
        {"name": "N Mahto", "team": "CDQ", "role": "bowl", "credits": 7.0},
        {"name": "C Yadav", "team": "CDQ", "role": "bowl", "credits": 7.0},
        {"name": "P Halder", "team": "CDQ", "role": "bowl", "credits": 7.0},
        {"name": "S Yadav", "team": "CDQ", "role": "bowl", "credits": 6.5},
        {"name": "S Soni", "team": "CDQ", "role": "bowl", "credits": 6.5},
        {"name": "Jyoti", "team": "CDQ", "role": "bowl", "credits": 6.5}
    ]
    
    mock_data = {9000 + i: {'name': p['name'], 'credits': p['credits'], 'team': p['team'], 'role': p['role']} for i, p in enumerate(authentic_roster)}
    df = pd.DataFrame.from_dict(mock_data, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'player_id'}, inplace=True)
    return df


# ==========================================
# 2. LINEUP GENERATOR ENGINE (ORGANIC SOLVER)
# ==========================================
def generate_dream11_team(df):
    print("\n--- RUNNING LINEUP OPTIMIZER (CDQ-W vs SDS-W) ---")
    df = calculate_player_ev(df, toss_decision="bowl", venue_type="bowling")
    
    # Secure balanced candidate pool across all positions
    top_wks = df[df['role'] == 'wk'].sort_values(by='projected_points', ascending=False).head(2)
    top_bats = df[df['role'] == 'bat'].sort_values(by='projected_points', ascending=False).head(6)
    top_ars = df[df['role'] == 'ar'].sort_values(by='projected_points', ascending=False).head(8)
    top_bowls = df[df['role'] == 'bowl'].sort_values(by='projected_points', ascending=False).head(8)
    
    df = pd.concat([top_wks, top_bats, top_ars, top_bowls]).drop_duplicates(subset=['player_id']).reset_index(drop=True)
    
    prob = LpProblem("CDQ_SDS_Optimization", LpMaximize)
    player_vars = {pid: LpVariable(f"player_{pid}", cat="Binary") for pid in df['player_id']}
        
    prob += lpSum(df[df['player_id'] == pid]['projected_points'].values[0] * player_vars[pid] for pid in df['player_id'])
    
    prob += lpSum(player_vars[pid] for pid in df['player_id']) == 11
    prob += lpSum(df[df['player_id'] == pid]['credits'].values[0] * player_vars[pid] for pid in df['player_id']) <= 100
    
    teams = df['team'].unique()
    if len(teams) >= 2:
        team_a_pids = df[df['team'] == teams[0]]['player_id'].tolist()
        prob += lpSum(player_vars[pid] for pid in team_a_pids) <= 7
        prob += lpSum(player_vars[pid] for pid in team_a_pids) >= 4 
    
    for role, (min_c, max_c) in [('wk', (1, 2)), ('bat', (3, 5)), ('ar', (1, 4)), ('bowl', (3, 5))]:
        role_pids = df[df['role'] == role]['player_id'].tolist()
        if role_pids: 
            prob += lpSum(player_vars[pid] for pid in role_pids) >= min_c
            prob += lpSum(player_vars[pid] for pid in role_pids) <= max_c

    premium_pids = df[df['projected_points'] >= 45.0]['player_id'].tolist()
    if len(premium_pids) >= 3:
        prob += lpSum(player_vars[pid] for pid in premium_pids) >= 3
    
    prob.solve(PULP_CBC_CMD(msg=False))
    
    selected_players = [df[df['player_id'] == pid].iloc[0] for pid in df['player_id'] if player_vars[pid].value() == 1.0]
    final_team_df = pd.DataFrame(selected_players)
    
    if final_team_df.empty:
        return final_team_df, 0.0, 0.0

    # ORGANIC C/VC SELECTION: Strictly sort by projected points highest to lowest
    final_team_df = final_team_df.sort_values(by='projected_points', ascending=False).reset_index(drop=True)
    labels, final_points = [], []
    
    for i, row in final_team_df.iterrows():
        if i == 0:
            labels.append('C')  # Rank 1 gets organic Captaincy
            final_points.append(row['projected_points'] * 2.0)
        elif i == 1:
            labels.append('VC') # Rank 2 gets organic Vice-Captaincy
            final_points.append(row['projected_points'] * 1.5)
        else:
            labels.append('')
            final_points.append(row['projected_points'])
            
    final_team_df['Multiplier'] = labels
    final_team_df['Final_EV'] = final_points
    
    return final_team_df, sum(final_team_df['credits']), sum(final_team_df['Final_EV'])


# ==========================================
# 3. PLOTLY DASHBOARD (ORGANIC C/VC DASHBOARD)
# ==========================================
def render_plotly_dashboard(final_team_df):
    plot_df = final_team_df.sort_values(by='Final_EV', ascending=True)
    fig = px.bar(
        plot_df, x='Final_EV', y='name', color='role', orientation='h',
        title="CDQ-W vs SDS-W: Organic Model-Driven C/VC Dashboard",
        hover_data=['team', 'credits', 'Multiplier', 'base_score', 'projected_points'],
        labels={'Final_EV': 'Vegas Projected Final Points (Organic Scaling)', 'name': 'Player'}
    )
    fig.add_vline(x=45, line_dash="dash", line_color="red", annotation_text="Vegas 45+ Anchor Line")
    fig.update_layout(template="plotly_dark")
    
    file_path = os.path.normpath(r"C:\Users\User\OneDrive\Desktop\Cricket\cdq_sds_dashboard.html")
    fig.write_html(file_path)
    try:
        os.startfile(file_path)
    except Exception:
        pass


# ==========================================
# 4. MAIN EXECUTION BLOCK
# ==========================================
if __name__ == "__main__":
    print("==========================================")
    print(" CDQ-W vs SDS-W: ORGANIC SOLVER RUN       ")
    print("==========================================\n")
    
    try:
        player_df = get_clean_dataframe()
        optimal_team, used_credits, ev_points = generate_dream11_team(player_df)
        
        print("\n=======================================================")
        print("  CDQ-W vs SDS-W: ORGANICALLY ASSIGNED C/VC XI         ")
        print("=======================================================")
        display_df = optimal_team[['Multiplier', 'name', 'team', 'role', 'credits', 'base_score', 'projected_points', 'Final_EV']]
        print(display_df.to_string(index=False, float_format="%.1f"))
        print("-------------------------------------------------------")
        print(f"Total Credits Used: {used_credits:.1f} / 100")
        print(f"Total Projected EV: {ev_points:.1f}")
        print("=======================================================\n")
        
        render_plotly_dashboard(optimal_team)
        
        csv_path = os.path.normpath(r"C:\Users\User\OneDrive\Desktop\Cricket\CDQ_SDS_Optimal_XI.csv")
        optimal_team[['Multiplier', 'name', 'team', 'role', 'credits', 'Final_EV']].to_csv(csv_path, index=False)

    except Exception as err:
        print(f"\n[!] Execution Error: {err}")
