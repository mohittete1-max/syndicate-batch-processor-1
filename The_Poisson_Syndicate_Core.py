import os
import math
import pandas as pd
import plotly.express as px
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD

# ==========================================
# 1. POISSON DISTRIBUTION MODELING
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

# ==========================================
# 2. MATCH POOL DATA (TEMPLATE / ACTIVE MATCH)
# ==========================================
# This serves as your base template. Update player pools per match.
match_players = [
    {"player_id": 1,  "name": "Player A1", "team": "TEAM1", "role": "ar",   "credits": 7.5, "form_pts": 250},
    {"player_id": 2,  "name": "Player A2", "team": "TEAM1", "role": "wk",   "credits": 6.5, "form_pts": 210},
    {"player_id": 3,  "name": "Player A3", "team": "TEAM1", "role": "bat",  "credits": 8.0, "form_pts": 300},
    {"player_id": 4,  "name": "Player A4", "team": "TEAM1", "role": "bat",  "credits": 7.0, "form_pts": 150},
    {"player_id": 5,  "name": "Player A5", "team": "TEAM1", "role": "bat",  "credits": 8.5, "form_pts": 320},
    {"player_id": 6,  "name": "Player A6", "team": "TEAM1", "role": "ar",   "credits": 6.5, "form_pts": 230},
    {"player_id": 7,  "name": "Player A7", "team": "TEAM1", "role": "bowl", "credits": 6.5, "form_pts": 410},
    {"player_id": 8,  "name": "Player A8", "team": "TEAM1", "role": "bowl", "credits": 8.0, "form_pts": 290},
    {"player_id": 9,  "name": "Player A9", "team": "TEAM1", "role": "bowl", "credits": 7.5, "form_pts": 330},
    {"player_id": 10, "name": "Player A10","team": "TEAM1", "role": "bowl", "credits": 8.5, "form_pts": 240},
    {"player_id": 11, "name": "Player A11","team": "TEAM1", "role": "bat",  "credits": 7.5, "form_pts": 190},
    
    {"player_id": 12, "name": "Player B1", "team": "TEAM2", "role": "wk",   "credits": 7.5, "form_pts": 180},
    {"player_id": 13, "name": "Player B2", "team": "TEAM2", "role": "wk",   "credits": 7.5, "form_pts": 450},
    {"player_id": 14, "name": "Player B3", "team": "TEAM2", "role": "bat",  "credits": 7.0, "form_pts": 120},
    {"player_id": 15, "name": "Player B4", "team": "TEAM2", "role": "wk",   "credits": 7.5, "form_pts": 210},
    {"player_id": 16, "name": "Player B5", "team": "TEAM2", "role": "ar",   "credits": 7.0, "form_pts": 190},
    {"player_id": 17, "name": "Player B6", "team": "TEAM2", "role": "bat",  "credits": 7.0, "form_pts": 160},
    {"player_id": 18, "name": "Player B7", "team": "TEAM2", "role": "bowl", "credits": 7.5, "form_pts": 310},
    {"player_id": 19, "name": "Player B8", "team": "TEAM2", "role": "bowl", "credits": 8.0, "form_pts": 250},
    {"player_id": 20, "name": "Player B9", "team": "TEAM2", "role": "bowl", "credits": 7.0, "form_pts": 190},
    {"player_id": 21, "name": "Player B10","team": "TEAM2", "role": "bowl", "credits": 8.0, "form_pts": 180},
    {"player_id": 22, "name": "Player B11","team": "TEAM2", "role": "bowl", "credits": 8.0, "form_pts": 220}
]

df = pd.DataFrame(match_players)

# ==========================================
# 3. EXPECTED VALUE CALCULATIONS
# ==========================================
projected_ev = []
for _, row in df.iterrows():
    role = row['role']
    cr_factor = row['credits'] / 8.5
    form_weight = 1.0 + (row['form_pts'] / 2000.0)

    if role in ['bat', 'wk']:
        lambda_r = cr_factor * 22.0 * form_weight
        ev = calculate_batting_ev(lambda_r)
    elif role == 'bowl':
        lambda_w = cr_factor * 1.35 * form_weight
        ev = calculate_bowling_ev(max(lambda_w, 0.1))
    elif role == 'ar':
        lambda_r = cr_factor * 14.0 * form_weight
        lambda_w = cr_factor * 1.05 * form_weight
        ev = calculate_batting_ev(lambda_r) + calculate_bowling_ev(max(lambda_w, 0.1))

    ev += 4.0
    projected_ev.append(round(ev, 1))

df['projected_points'] = projected_ev

# ==========================================
# 4. INTEGER LINEAR PROGRAMMING (PULP)
# ==========================================
prob = LpProblem("Universal_Syndicate_Optimization", LpMaximize)
player_vars = {row['player_id']: LpVariable(f"p_{row['player_id']}", cat="Binary") for _, row in df.iterrows()}

# Objective Function: Maximize Expected Points
prob += lpSum(row['projected_points'] * player_vars[row['player_id']] for _, row in df.iterrows())

# Core Squad Size & Budget Constraints
prob += lpSum(player_vars[pid] for pid in player_vars) == 11
prob += lpSum(df[df['player_id'] == pid]['credits'].values[0] * player_vars[pid] for pid in player_vars) <= 100.0

# ==========================================
# 5. MODERN FLEXIBLE ROSTER CONSTRAINTS
# ==========================================
# Flexible Team Stacking (Min 1, Max 10 per team)
for t in df['team'].unique():
    t_pids = df[df['team'] == t]['player_id'].tolist()
    prob += lpSum(player_vars[pid] for pid in t_pids) <= 10
    prob += lpSum(player_vars[pid] for pid in t_pids) >= 1

# Flexible Role Quotas (Min 1, Max 8 per role)
for r in ['wk', 'bat', 'ar', 'bowl']:
    r_pids = df[df['role'] == r]['player_id'].tolist()
    prob += lpSum(player_vars[pid] for pid in r_pids) >= 1
    prob += lpSum(player_vars[pid] for pid in r_pids) <= 8

# ==========================================
# 6. VEGAS CASINO RULE (3-PILLAR ANCHOR)
# ==========================================
anchor_threshold = 45.0
anchor_pids = df[df['projected_points'] >= anchor_threshold]['player_id'].tolist()
if len(anchor_pids) >= 3:
    prob += lpSum(player_vars[pid] for pid in anchor_pids) >= 3

# Solve the optimization problem
prob.solve(PULP_CBC_CMD(msg=False))

# ==========================================
# 7. OUTPUT GENERATION & DASHBOARD
# ==========================================
selected_pids = [pid for pid in player_vars if player_vars[pid].value() == 1.0]
final_team = df[df['player_id'].isin(selected_pids)].copy()
final_team = final_team.sort_values(by='projected_points', ascending=False).reset_index(drop=True)

labels, final_ev = [], []
for idx, row in final_team.iterrows():
    if idx == 0:
        labels.append('C')
        final_ev.append(row['projected_points'] * 2.0)
    elif idx == 1:
        labels.append('VC')
        final_ev.append(row['projected_points'] * 1.5)
    else:
        labels.append('')
        final_ev.append(row['projected_points'])

final_team['Multiplier'] = labels
final_team['Final_EV'] = final_ev

print("\n=======================================================")
print("      UNIVERSAL SYNDICATE OPTIMAL XI (FLEXIBLE)        ")
print("=======================================================")
print(final_team[['Multiplier', 'name', 'team', 'role', 'credits', 'projected_points', 'Final_EV']].to_string(index=False))
print("-------------------------------------------------------")
print(f"Total Credits Used: {final_team['credits'].sum():.1f} / 100.0")
print(f"Total Projected EV: {final_team['Final_EV'].sum():.1f}")
print("=======================================================\n")

out_dir = r"C:\Users\User\OneDrive\Desktop\Cricket"
final_team.to_csv(os.path.join(out_dir, "Universal_Optimal_XI.csv"), index=False)

fig = px.bar(
    final_team.sort_values(by='Final_EV', ascending=True),
    x='Final_EV',
    y='name',
    color='role',
    orientation='h',
    title="Universal Syndicate Optimal XI (Flexible Stacking & Vegas Anchors)",
    hover_data=['team', 'credits', 'Multiplier', 'projected_points']
)
fig.update_layout(template="plotly_dark")
html_path = os.path.join(out_dir, "universal_optimal_dashboard.html")
fig.write_html(html_path)

try:
    os.startfile(html_path)
except Exception:
    pass
