import os
import math
import webbrowser
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD

# ==========================================
# 1. GLOBAL CONFIGURATION & RENDERER SETUP
# ==========================================
pio.renderers.default = "browser"

ENTRY_FEE = 49
ENTRY_MODE = "Single Bullet (1 Team)"
ENGINE_NAME = "Universal Syndicate Protocol"
CSV_OUTPUT_NAME = "Single_Bullet_Optimal_XI.csv"
DASHBOARD_NAME = "single_bullet_dashboard.html"
OUTPUT_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"

# ==========================================
# 2. POISSON DISTRIBUTION MODELING
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
# 3. ACTIVE MATCH POOL DATA (RTD vs ADF)
# ==========================================
match_players = [
    # --- Rotterdam Dockers (RTD) ---
    {"player_id": 1,  "name": "F du Plessis",         "team": "RTD", "role": "bat",  "credits": 9.0, "form_pts": 340},
    {"player_id": 2,  "name": "Heinrich Klaasen",     "team": "RTD", "role": "wk",   "credits": 9.0, "form_pts": 380},
    {"player_id": 3,  "name": "Ben McDermott",        "team": "RTD", "role": "wk",   "credits": 8.5, "form_pts": 270},
    {"player_id": 4,  "name": "Logan van Beek",       "team": "RTD", "role": "ar",   "credits": 8.5, "form_pts": 310},
    {"player_id": 5,  "name": "Anrich Nortje",        "team": "RTD", "role": "bowl", "credits": 8.5, "form_pts": 350},
    {"player_id": 6,  "name": "Michael Levitt",       "team": "RTD", "role": "bat",  "credits": 7.5, "form_pts": 210},
    {"player_id": 7,  "name": "Ben Manenti",          "team": "RTD", "role": "ar",   "credits": 7.0, "form_pts": 195},
    {"player_id": 8,  "name": "Sandeep Lamichhane",   "team": "RTD", "role": "bowl", "credits": 8.0, "form_pts": 320},
    {"player_id": 9,  "name": "David Wiese",          "team": "RTD", "role": "ar",   "credits": 8.0, "form_pts": 260},
    {"player_id": 10, "name": "Vikramjit Singh",      "team": "RTD", "role": "bat",  "credits": 7.5, "form_pts": 180},
    {"player_id": 11, "name": "Roelof van der Merwe", "team": "RTD", "role": "ar",   "credits": 7.5, "form_pts": 245},

    # --- Amsterdam Flames (ADF) ---
    {"player_id": 12, "name": "Mitchell Marsh",       "team": "ADF", "role": "ar",   "credits": 9.0, "form_pts": 410},
    {"player_id": 13, "name": "Steve Smith",          "team": "ADF", "role": "bat",  "credits": 9.0, "form_pts": 360},
    {"player_id": 14, "name": "Tim David",            "team": "ADF", "role": "bat",  "credits": 8.5, "form_pts": 290},
    {"player_id": 15, "name": "Scott Edwards",        "team": "ADF", "role": "wk",   "credits": 8.0, "form_pts": 240},
    {"player_id": 16, "name": "Bas de Leede",         "team": "ADF", "role": "ar",   "credits": 8.0, "form_pts": 280},
    {"player_id": 17, "name": "Curtis Campher",       "team": "ADF", "role": "ar",   "credits": 7.5, "form_pts": 225},
    {"player_id": 18, "name": "Richard Gleeson",      "team": "ADF", "role": "bowl", "credits": 8.0, "form_pts": 305},
    {"player_id": 19, "name": "David Payne",          "team": "ADF", "role": "bowl", "credits": 7.5, "form_pts": 250},
    {"player_id": 20, "name": "Aryan Dutt",           "team": "ADF", "role": "bowl", "credits": 7.0, "form_pts": 200},
    {"player_id": 21, "name": "Max O'Dowd",           "team": "ADF", "role": "bat",  "credits": 7.5, "form_pts": 215},
    {"player_id": 22, "name": "Michael Bracewell",    "team": "ADF", "role": "ar",   "credits": 7.5, "form_pts": 235}
]

df = pd.DataFrame(match_players)

# ==========================================
# 4. EXPECTED VALUE CALCULATIONS
# ==========================================
projected_ev = []
for _, row in df.iterrows():
    role = row['role']
    cr_factor = row['credits'] / 9.0
    form_weight = 1.0 + (row['form_pts'] / 2000.0)

    if role in ['bat', 'wk']:
        lambda_r = cr_factor * 23.0 * form_weight
        ev = calculate_batting_ev(lambda_r)
    elif role == 'bowl':
        lambda_w = cr_factor * 1.40 * form_weight
        ev = calculate_bowling_ev(max(lambda_w, 0.1))
    elif role == 'ar':
        lambda_r = cr_factor * 15.0 * form_weight
        lambda_w = cr_factor * 1.10 * form_weight
        ev = calculate_batting_ev(lambda_r) + calculate_bowling_ev(max(lambda_w, 0.1))

    ev += 4.0
    projected_ev.append(round(ev, 1))

df['projected_points'] = projected_ev

# ==========================================
# 5. INTEGER LINEAR PROGRAMMING (PULP)
# ==========================================
prob = LpProblem("Universal_Syndicate_Optimization", LpMaximize)
player_vars = {row['player_id']: LpVariable(f"p_{row['player_id']}", cat="Binary") for _, row in df.iterrows()}

# Objective Function: Maximize Expected Points
prob += lpSum(row['projected_points'] * player_vars[row['player_id']] for _, row in df.iterrows())

# Core Squad Size & Budget Constraints
prob += lpSum(player_vars[pid] for pid in player_vars) == 11
prob += lpSum(df[df['player_id'] == pid]['credits'].values[0] * player_vars[pid] for pid in player_vars) <= 100.0

# Flexible Stacking Constraints (1 to 10 per team, 1 to 8 per role)
for t in df['team'].unique():
    t_pids = df[df['team'] == t]['player_id'].tolist()
    prob += lpSum(player_vars[pid] for pid in t_pids) <= 10
    prob += lpSum(player_vars[pid] for pid in t_pids) >= 1

for r in ['wk', 'bat', 'ar', 'bowl']:
    r_pids = df[df['role'] == r]['player_id'].tolist()
    prob += lpSum(player_vars[pid] for pid in r_pids) >= 1
    prob += lpSum(player_vars[pid] for pid in r_pids) <= 8

# ==========================================
# 6. VEGAS CASINO 3-ANCHOR RULE
# ==========================================
anchor_threshold = 45.0
anchor_pids = df[df['projected_points'] >= anchor_threshold]['player_id'].tolist()
anchor_applied = False
if len(anchor_pids) >= 3:
    prob += lpSum(player_vars[pid] for pid in anchor_pids) >= 3
    anchor_applied = True

# Solve
prob.solve(PULP_CBC_CMD(msg=False))

# ==========================================
# 7. BUILD FINAL TEAM DATAFRAME
# ==========================================
selected_pids = [pid for pid in player_vars if player_vars[pid].value() == 1.0]
final_team = df[df['player_id'].isin(selected_pids)].copy()
final_team = final_team.sort_values(by='projected_points', ascending=False).reset_index(drop=True)

# Assign Multipliers (C = 2x, VC = 1.5x)
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

# ==========================================
# 8. SYNDICATE TERMINAL OUTPUT & ARCHIVAL
# ==========================================
print("\n=======================================================")
print("      UNIVERSAL SYNDICATE OPTIMAL XI (FLEXIBLE)        ")
print(f"      Engine: {ENGINE_NAME} | Mode: {ENTRY_MODE}       ")
print(f"      Target: ${ENTRY_FEE} GPP Pool                     ")
print("=======================================================")
print(final_team[['Multiplier', 'name', 'team', 'role', 'credits', 'projected_points', 'Final_EV']].to_string(index=False))
print("-------------------------------------------------------")
print(f"Vegas 3-Anchor Rule: {'LOCKED (>= 3 High-EV Anchors Enforced)' if anchor_applied else 'BYPASSED (< 3 Eligible in Pool)'}")
print(f"Total Credits Used : {final_team['credits'].sum():.1f} / 100.0")
print(f"Total Projected EV : {final_team['Final_EV'].sum():.1f}")
print("=======================================================\n")

os.makedirs(OUTPUT_DIR, exist_ok=True)
final_team.to_csv(os.path.join(OUTPUT_DIR, CSV_OUTPUT_NAME), index=False)

# ==========================================
# 9. DARK-THEME PLOTLY DASHBOARD LAUNCH
# ==========================================
fig = px.bar(
    final_team.sort_values(by='Final_EV', ascending=True),
    x='Final_EV',
    y='name',
    color='role',
    orientation='h',
    title=f"Universal Syndicate Optimal XI ({ENTRY_MODE} - ${ENTRY_FEE} Target)",
    hover_data=['team', 'credits', 'Multiplier', 'projected_points'],
    color_discrete_map={
        'ar': '#a855f7',    # Syndicate Purple
        'bowl': '#10b981',  # Forest Emerald
        'bat': '#3b82f6',   # Sky Blue
        'wk': '#ef4444'     # Coral Crimson
    }
)

fig.update_layout(
    template="plotly_dark",
    xaxis_title="Final Projected Expected Value (EV)",
    yaxis_title="Player Name",
    font=dict(family="Segoe UI, sans-serif", size=12),
    plot_bgcolor="#111827",
    paper_bgcolor="#111827"
)

html_path = os.path.join(OUTPUT_DIR, DASHBOARD_NAME)
fig.write_html(html_path, auto_open=False)

# Direct browser launch via normalized system URL
webbrowser.open(f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}")
