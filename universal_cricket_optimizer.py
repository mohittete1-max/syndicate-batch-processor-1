import os
import math
import webbrowser
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD

# Import live environmental intelligence module
from global_pitch import get_complete_match_environment

# ==========================================
# 1. LIVE MATCH ENVIRONMENT INITIALIZATION
# ==========================================
ACTIVE_VENUE = "Sportpark Westvliet, The Hague"

# Automatically pull venue baseline + live weather API metrics
env = get_complete_match_environment(ACTIVE_VENUE)
PITCH_TYPE = env["pitch_type"]
ANCHOR_THRESHOLD = env["threshold"]
WEATHER_CONDITION = env["weather"]

pio.renderers.default = "browser"

ENTRY_FEE = 49
ENTRY_MODE = "Single Bullet (1 Team)"
ENGINE_NAME = "Universal Syndicate Protocol v3.3 (Strict Compliance)"
CSV_OUTPUT_NAME = "Single_Bullet_Optimal_XI.csv"
DASHBOARD_NAME = "single_bullet_dashboard.html"
OUTPUT_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"

print(f"[{'LIVE API ACTIVE' if env['is_live'] else 'OFFLINE FALLBACK'}] Venue: {env['venue']}")
print(f"Conditions -> Weather: {env['weather']} | Temp: {env['temp']}°C | Humidity: {env['humidity']}%")
print(f"Active Pitch Profile: {PITCH_TYPE} | Dynamic Threshold: {ANCHOR_THRESHOLD}pt\n")

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
# 3. ACTIVE MATCH ROSTER & STATUS VALIDATION
# ==========================================
match_players = [
    # --- Rotterdam Dockers (RTD) ---
    {"player_id": 1,  "name": "F du Plessis",         "team": "RTD", "role": "bat",  "credits": 9.0, "form_pts": 340, "status": "Playing"},
    {"player_id": 2,  "name": "Heinrich Klaasen",     "team": "RTD", "role": "wk",   "credits": 9.0, "form_pts": 380, "status": "Playing"},
    {"player_id": 3,  "name": "Ben McDermott",        "team": "RTD", "role": "wk",   "credits": 8.5, "form_pts": 270, "status": "Playing"},
    {"player_id": 4,  "name": "Logan van Beek",       "team": "RTD", "role": "ar",   "credits": 8.5, "form_pts": 310, "status": "Playing"},
    {"player_id": 5,  "name": "Anrich Nortje",        "team": "RTD", "role": "bowl", "credits": 8.5, "form_pts": 350, "status": "Playing"},
    {"player_id": 6,  "name": "Michael Levitt",       "team": "RTD", "role": "bat",  "credits": 7.5, "form_pts": 210, "status": "Playing"},
    {"player_id": 7,  "name": "Ben Manenti",          "team": "RTD", "role": "ar",   "credits": 7.0, "form_pts": 195, "status": "Playing"},
    {"player_id": 8,  "name": "Sandeep Lamichhane",   "team": "RTD", "role": "bowl", "credits": 8.0, "form_pts": 320, "status": "Playing"},
    {"player_id": 9,  "name": "David Wiese",          "team": "RTD", "role": "ar",   "credits": 8.0, "form_pts": 260, "status": "Playing"},
    {"player_id": 10, "name": "Vikramjit Singh",      "team": "RTD", "role": "bat",  "credits": 7.5, "form_pts": 180, "status": "Playing"},
    {"player_id": 11, "name": "Roelof van der Merwe", "team": "RTD", "role": "ar",   "credits": 7.5, "form_pts": 245, "status": "Playing"},

    # --- Amsterdam Flames (ADF) ---
    {"player_id": 12, "name": "Mitchell Marsh",       "team": "ADF", "role": "ar",   "credits": 9.0, "form_pts": 410, "status": "Playing"},
    {"player_id": 13, "name": "Steve Smith",          "team": "ADF", "role": "bat",  "credits": 9.0, "form_pts": 360, "status": "Playing"},
    {"player_id": 14, "name": "Tim David",            "team": "ADF", "role": "bat",  "credits": 8.5, "form_pts": 290, "status": "Playing"},
    {"player_id": 15, "name": "Scott Edwards",        "team": "ADF", "role": "wk",   "credits": 8.0, "form_pts": 240, "status": "Playing"},
    {"player_id": 16, "name": "Bas de Leede",         "team": "ADF", "role": "ar",   "credits": 8.0, "form_pts": 280, "status": "Playing"},
    {"player_id": 17, "name": "Curtis Campher",       "team": "ADF", "role": "ar",   "credits": 7.5, "form_pts": 225, "status": "Playing"},
    {"player_id": 18, "name": "Richard Gleeson",      "team": "ADF", "role": "bowl", "credits": 8.0, "form_pts": 305, "status": "Playing"},
    {"player_id": 19, "name": "David Payne",          "team": "ADF", "role": "bowl", "credits": 7.5, "form_pts": 250, "status": "Playing"},
    {"player_id": 20, "name": "Aryan Dutt",           "team": "ADF", "role": "bowl", "credits": 7.0, "form_pts": 200, "status": "Playing"},
    {"player_id": 21, "name": "Max O'Dowd",           "team": "ADF", "role": "bat",  "credits": 7.5, "form_pts": 215, "status": "Playing"},
    {"player_id": 22, "name": "Michael Bracewell",    "team": "ADF", "role": "ar",   "credits": 7.5, "form_pts": 235, "status": "Playing"}
]

raw_df = pd.DataFrame(match_players)
df = raw_df[raw_df['status'] == 'Playing'].copy()

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

    # Weather & Condition Modifiers
    if WEATHER_CONDITION == "Overcast / Seamer Friendly" and role == 'bowl':
        ev *= 1.15
    elif WEATHER_CONDITION == "Dew Factor" and role in ['bat', 'wk']:
        ev *= 1.10

    ev += 4.0
    projected_ev.append(round(ev, 1))

df['projected_points'] = projected_ev

# ==========================================
# 5. STRICT DREAM11 COMPLIANCE LINEUP SOLVER
# ==========================================
def solve_lineup(script_name, focus_constraint_func=None):
    prob = LpProblem(f"Syndicate_{script_name}", LpMaximize)
    player_vars = {row['player_id']: LpVariable(f"p_{row['player_id']}", cat="Binary") for _, row in df.iterrows()}

    # Objective Function: Maximize Total Projected EV
    prob += lpSum(row['projected_points'] * player_vars[row['player_id']] for _, row in df.iterrows())

    # Core Dream11 Size Constraint: Exactly 11 Players
    prob += lpSum(player_vars[pid] for pid in player_vars) == 11

    # Credit Cap Constraint: Max 100 Credits
    prob += lpSum(df[df['player_id'] == pid]['credits'].values[0] * player_vars[pid] for pid in player_vars) <= 100.0

    # Strict Per-Team Cap (Max 7 players from a single team per rules)
    for t in df['team'].unique():
        t_pids = df[df['team'] == t]['player_id'].tolist()
        prob += lpSum(player_vars[pid] for pid in t_pids) <= 7
        prob += lpSum(player_vars[pid] for pid in t_pids) >= 1

    # Strict Role Constraints (Dream11 Platform Limits)
    role_limits = {
        'wk': (1, 4),   # Exactly 1 to 4 Wicket-Keepers
        'bat': (1, 6),  # 1 to 6 Batters
        'ar': (1, 6),   # 1 to 6 All-Rounders
        'bowl': (1, 6)  # 1 to 6 Bowlers
    }

    for r, (min_lim, max_lim) in role_limits.items():
        r_pids = df[df['role'] == r]['player_id'].tolist()
        if r_pids:
            prob += lpSum(player_vars[pid] for pid in r_pids) >= min_lim
            prob += lpSum(player_vars[pid] for pid in r_pids) <= max_lim

    # Dynamic Vegas 3-Anchor Rule
    anchor_pids = df[df['projected_points'] >= ANCHOR_THRESHOLD]['player_id'].tolist()
    anchor_locked = False
    if len(anchor_pids) >= 3:
        prob += lpSum(player_vars[pid] for pid in anchor_pids) >= 3
        anchor_locked = True

    # Custom Script Modifier if supplied
    if focus_constraint_func:
        focus_constraint_func(prob, player_vars, df)

    prob.solve(PULP_CBC_CMD(msg=False))

    # Extract clean binary selections
    selected_pids = [pid for pid in player_vars if player_vars[pid].value() is not None and player_vars[pid].value() > 0.5]
    res_team = df[df['player_id'].isin(selected_pids)].copy()
    res_team = res_team.sort_values(by='projected_points', ascending=False).reset_index(drop=True)
    return res_team, anchor_locked

final_team, is_anchored = solve_lineup("Macro_Baseline")

def slugfest_modifier(prob, p_vars, data):
    bowl_pids = data[data['role'].isin(['bowl', 'ar'])]['player_id'].tolist()
    prob += lpSum(p_vars[pid] for pid in bowl_pids) >= 7

alt_team, _ = solve_lineup("Bowling_Slugfest", slugfest_modifier)

# ==========================================
# 6. MULTIPLIER ASSIGNMENT
# ==========================================
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
# 7. TERMINAL OUTPUT & ARCHIVAL
# ==========================================
print("\n=======================================================")
print(f"      {ENGINE_NAME} - {ENTRY_MODE.upper()}           ")
print(f"      Venue: {ACTIVE_VENUE} | Pitch: {PITCH_TYPE} | Weather: {WEATHER_CONDITION}")
print("=======================================================")
print(final_team[['Multiplier', 'name', 'team', 'role', 'credits', 'projected_points', 'Final_EV']].to_string(index=False))
print("-------------------------------------------------------")
print(f"Vegas 3-Anchor Rule  : {'LOCKED (Enforced)' if is_anchored else 'BYPASSED'}")
print(f"Shadow Script Check  : Slugfest EV -> {alt_team['projected_points'].sum():.1f}")
print(f"Total Credits Used   : {final_team['credits'].sum():.1f} / 100.0")
print(f"Total Projected EV   : {final_team['Final_EV'].sum():.1f}")
print("=======================================================\n")

os.makedirs(OUTPUT_DIR, exist_ok=True)
final_team.to_csv(os.path.join(OUTPUT_DIR, CSV_OUTPUT_NAME), index=False)

# ==========================================
# 8. PLOTLY DASHBOARD RENDERER
# ==========================================
fig = px.bar(
    final_team.sort_values(by='Final_EV', ascending=True),
    x='Final_EV',
    y='name',
    color='role',
    orientation='h',
    title=f"Single Bullet Compliance XI ({ACTIVE_VENUE})",
    hover_data=['team', 'credits', 'Multiplier', 'projected_points'],
    color_discrete_map={'ar': '#a855f7', 'bowl': '#10b981', 'bat': '#3b82f6', 'wk': '#ef4444'}
)
fig.update_layout(template="plotly_dark", xaxis_title="Final Projected EV", yaxis_title="Player Name")
html_path = os.path.join(OUTPUT_DIR, DASHBOARD_NAME)
fig.write_html(html_path, auto_open=False)
webbrowser.open(f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}")
