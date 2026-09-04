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
# 2. CONFIRMED STARTING XI POOL (POST-TOSS)
# ==========================================
confirmed_players = [
    # --- Lyca Kovai Kings (LKK - Bowling 1st) ---
    {"player_id": 1,  "name": "S Radhakrishnan",  "team": "LKK", "role": "ar",   "credits": 6.5, "form_pts": 193},
    {"player_id": 2,  "name": "S Lokeshwar",      "team": "LKK", "role": "wk",   "credits": 6.5, "form_pts": 213},
    {"player_id": 3,  "name": "B Sachin",         "team": "LKK", "role": "bat",  "credits": 8.0, "form_pts": 356},
    {"player_id": 4,  "name": "A Siddharth",      "team": "LKK", "role": "bat",  "credits": 7.0, "form_pts": 54},
    {"player_id": 5,  "name": "S Khan",           "team": "LKK", "role": "bat",  "credits": 8.5, "form_pts": 320},
    {"player_id": 6,  "name": "G Kishoor",        "team": "LKK", "role": "ar",   "credits": 6.5, "form_pts": 237},
    {"player_id": 7,  "name": "J Subramanyan",    "team": "LKK", "role": "bowl", "credits": 6.5, "form_pts": 418},
    {"player_id": 8,  "name": "M Prasad",         "team": "LKK", "role": "wk",   "credits": 6.0, "form_pts": 125},
    {"player_id": 9,  "name": "K Deeban Lingesh", "team": "LKK", "role": "ar",   "credits": 7.5, "form_pts": 285},
    {"player_id": 10, "name": "M Siddharth",     "team": "LKK", "role": "bowl", "credits": 7.5, "form_pts": 336},
    {"player_id": 11, "name": "R Ambrish",        "team": "LKK", "role": "bowl", "credits": 8.5, "form_pts": 248},

    # --- IDream Tiruppur Tamizhans (ITT - Batting 1st) ---
    {"player_id": 12, "name": "A Sathvik-VP",     "team": "ITT", "role": "wk",   "credits": 7.5, "form_pts": 84},
    {"player_id": 13, "name": "T Raheja",         "team": "ITT", "role": "wk",   "credits": 7.5, "form_pts": 454},
    {"player_id": 14, "name": "K-Wafar",          "team": "ITT", "role": "bat",  "credits": 7.0, "form_pts": 22},
    {"player_id": 15, "name": "P Ranjan Paul",    "team": "ITT", "role": "wk",   "credits": 7.5, "form_pts": 219},
    {"player_id": 16, "name": "S Mohamed Ali",    "team": "ITT", "role": "ar",   "credits": 7.0, "form_pts": 101},
    {"player_id": 17, "name": "U Sasidev",        "team": "ITT", "role": "bat",  "credits": 7.0, "form_pts": 60},
    {"player_id": 18, "name": "Mathivanan",       "team": "ITT", "role": "bowl", "credits": 7.5, "form_pts": 316},
    {"player_id": 19, "name": "S Mohan Prasath",  "team": "ITT", "role": "bowl", "credits": 8.0, "form_pts": 154},
    {"player_id": 20, "name": "R Silambarasan",   "team": "ITT", "role": "bowl", "credits": 7.0, "form_pts": 109},
    {"player_id": 21, "name": "P Raghavendra",    "team": "ITT", "role": "bowl", "credits": 8.0, "form_pts": 88},
    {"player_id": 22, "name": "T Natarajan",      "team": "ITT", "role": "bowl", "credits": 8.0, "form_pts": 176}
]

df = pd.DataFrame(confirmed_players)

# ==========================================
# 3. TACTICAL WEIGHTINGS & PROJECTIONS
# ==========================================
projected_ev = []
for _, row in df.iterrows():
    role = row['role']
    cr_factor = row['credits'] / 8.5
    team = row['team']
    form_weight = 1.0 + (row['form_pts'] / 2000.0)

    pitch_runs = 1.15 if team == 'ITT' else 1.10
    pitch_wickets = 1.20 if team == 'LKK' else 1.05

    if role in ['bat', 'wk']:
        lambda_r = cr_factor * 22.0 * pitch_runs * form_weight
        ev = calculate_batting_ev(lambda_r)
    elif role == 'bowl':
        lambda_w = cr_factor * 1.35 * pitch_wickets * form_weight
        ev = calculate_bowling_ev(max(lambda_w, 0.1))
    elif role == 'ar':
        lambda_r = cr_factor * 14.0 * pitch_runs * form_weight
        lambda_w = cr_factor * 1.05 * pitch_wickets * form_weight
        ev = calculate_batting_ev(lambda_r) + calculate_bowling_ev(max(lambda_w, 0.1))

    ev += 4.0
    projected_ev.append(round(ev, 1))

df['projected_points'] = projected_ev

# ==========================================
# 4. INTEGER LINEAR PROGRAMMING (PULP)
# ==========================================
prob = LpProblem("Post_Toss_Vegas_Optimization", LpMaximize)
player_vars = {row['player_id']: LpVariable(f"p_{row['player_id']}", cat="Binary") for _, row in df.iterrows()}

# Maximize Expected Value
prob += lpSum(row['projected_points'] * player_vars[row['player_id']] for _, row in df.iterrows())

# Roster & Budget Limits
prob += lpSum(player_vars[pid] for pid in player_vars) == 11
prob += lpSum(df[df['player_id'] == pid]['credits'].values[0] * player_vars[pid] for pid in player_vars) <= 100.0

# Team Limits (4 to 7 per side)
for t in ['LKK', 'ITT']:
    t_pids = df[df['team'] == t]['player_id'].tolist()
    prob += lpSum(player_vars[pid] for pid in t_pids) <= 7
    prob += lpSum(player_vars[pid] for pid in t_pids) >= 4

# Positional Constraints
for r, (min_c, max_c) in [('wk', (1, 4)), ('bat', (3, 6)), ('ar', (1, 4)), ('bowl', (3, 6))]:
    r_pids = df[df['role'] == r]['player_id'].tolist()
    prob += lpSum(player_vars[pid] for pid in r_pids) >= min_c
    prob += lpSum(player_vars[pid] for pid in r_pids) <= max_c

# ==========================================
# 5. VEGAS CASINO RULE (3-PILLAR ANCHOR)
# ==========================================
# Guarantees at least 3 high-EV anchors (>= 45.0 projected points)
anchor_threshold = 45.0
anchor_pids = df[df['projected_points'] >= anchor_threshold]['player_id'].tolist()

if len(anchor_pids) >= 3:
    prob += lpSum(player_vars[pid] for pid in anchor_pids) >= 3

# Solve
prob.solve(PULP_CBC_CMD(msg=False))

# ==========================================
# 6. RESULTS & DASHBOARD EXPORT
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
print("   POST-TOSS OPTIMAL XI (VEGAS ANCHOR RULE ACTIVE)     ")
print("=======================================================")
print(final_team[['Multiplier', 'name', 'team', 'role', 'credits', 'projected_points', 'Final_EV']].to_string(index=False))
print("-------------------------------------------------------")
print(f"Total Credits Used: {final_team['credits'].sum():.1f} / 100.0")
print(f"Total Projected EV: {final_team['Final_EV'].sum():.1f}")
print("=======================================================\n")

out_dir = r"C:\Users\User\OneDrive\Desktop\Cricket"
final_team.to_csv(os.path.join(out_dir, "LKK_ITT_Vegas_Optimal_XI.csv"), index=False)

fig = px.bar(
    final_team.sort_values(by='Final_EV', ascending=True),
    x='Final_EV',
    y='name',
    color='role',
    orientation='h',
    title="LKK vs ITT Optimal XI (Vegas 3-Anchor Rule Enforced)",
    hover_data=['team', 'credits', 'Multiplier', 'projected_points']
)
fig.update_layout(template="plotly_dark")
html_path = os.path.join(out_dir, "lkk_itt_vegas_dashboard.html")
fig.write_html(html_path)

try:
    os.startfile(html_path)
except Exception:
    pass
