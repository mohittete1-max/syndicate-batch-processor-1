import os
import math
import webbrowser
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD

# ==========================================
# SAFE FALLBACK FOR LIVE ENVIRONMENT
# ==========================================
try:
    from global_pitch import get_complete_match_environment
except ImportError:
    def get_complete_match_environment(venue):
        return {
            "is_live": False,
            "venue": venue,
            "pitch_type": "Balanced / Standard",
            "threshold": 45.0,
            "weather": "Clear",
            "temp": 20,
            "humidity": 50
        }

# ==========================================
# 1. MATCH ENVIRONMENT & TOSS CONTROL
# ==========================================
ACTIVE_VENUE = "Sportpark Westvliet, The Hague"

# --- POST-TOSS INPUT (Update at Toss) ---
TOSS_WINNER = "RTD"       # Enter "RTD" or "ADF"
TOSS_DECISION = "Bowl"    # Enter "Bat" or "Bowl"

TEAM_1, TEAM_2 = "RTD", "ADF"
if TOSS_DECISION.strip().lower() == "bat":
    BATTING_FIRST = TOSS_WINNER
    BOWLING_FIRST = TEAM_2 if TOSS_WINNER == TEAM_1 else TEAM_1
else:
    BOWLING_FIRST = TOSS_WINNER
    BATTING_FIRST = TEAM_2 if TOSS_WINNER == TEAM_1 else TEAM_1

env = get_complete_match_environment(ACTIVE_VENUE)
PITCH_TYPE = env["pitch_type"]
ANCHOR_THRESHOLD = env["threshold"]
WEATHER_CONDITION = env["weather"]

pio.renderers.default = "browser"

ENGINE_NAME = "Universal Syndicate Protocol v3.7 (Dual Apex 1000+)"
OUTPUT_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"

print(f"[{'LIVE API ACTIVE' if env['is_live'] else 'OFFLINE FALLBACK'}] Venue: {env['venue']}")
print(f"Conditions -> Weather: {env['weather']} | Temp: {env['temp']}°C | Humidity: {env['humidity']}%")
print(f"Toss Script: {BATTING_FIRST} Batting 1st | {BOWLING_FIRST} Bowling 1st\n")

# ==========================================
# 2. POISSON DISTRIBUTION MODELING
# ==========================================
def poisson_probability(k, lambd):
    return (math.exp(-lambd) * (lambd ** k)) / math.factorial(k)

def calculate_batting_ev(expected_runs):
    base_points = expected_runs
    prob_duck = poisson_probability(0, expected_runs)
    prob_30_plus = 1.0 - sum(poisson_probability(k, expected_runs) for k in range(30))
    prob_50_plus = 1.0 - sum(poisson_probability(k, expected_runs) for k in range(50))
    return base_points + (-2.0 * prob_duck) + (4.0 * prob_30_plus) + (8.0 * prob_50_plus)

def calculate_bowling_ev(expected_wickets):
    base_points = expected_wickets * 25.0
    prob_3_plus = 1.0 - sum(poisson_probability(k, expected_wickets) for k in range(3))
    prob_4_plus = 1.0 - sum(poisson_probability(k, expected_wickets) for k in range(4))
    return base_points + (4.0 * prob_3_plus) + (8.0 * prob_4_plus)

# ==========================================
# 3. ACTIVE MATCH ROSTER & VALIDATION
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
# 4. 1000+ POINT EXPECTED VALUE CALCULATIONS
# ==========================================
projected_ev = []
for _, row in df.iterrows():
    role = row['role']
    team = row['team']
    cr_factor = row['credits'] / 9.0
    form_weight = 1.0 + (row['form_pts'] / 1100.0)

    if role in ['bat', 'wk']:
        lambda_r = cr_factor * 34.0 * form_weight
        ev = calculate_batting_ev(lambda_r) + (lambda_r * 0.9)
    elif role == 'bowl':
        lambda_w = cr_factor * 1.90 * form_weight
        ev = calculate_bowling_ev(max(lambda_w, 0.1)) + 18.0
    elif role == 'ar':
        lambda_r = cr_factor * 24.0 * form_weight
        lambda_w = cr_factor * 1.50 * form_weight
        ev = calculate_batting_ev(lambda_r) + calculate_bowling_ev(max(lambda_w, 0.1)) + (lambda_r * 0.7) + 15.0

    # Apply Post-Toss Modifiers
    if team == BOWLING_FIRST and role in ['bowl', 'ar']:
        ev *= 1.15
    elif team == BATTING_FIRST and role in ['bat', 'wk', 'ar']:
        ev *= 1.10

    # Weather Modifiers
    if WEATHER_CONDITION == "Overcast / Seamer Friendly" and role in ['bowl', 'ar']:
        ev *= 1.20
    elif WEATHER_CONDITION == "Dew Factor" and role in ['bat', 'wk']:
        ev *= 1.15

    ev += 10.0
    projected_ev.append(round(ev, 1))

df['projected_points'] = projected_ev

# ==========================================
# 5. LINEUP SOLVER & DUAL MULTIPLIER ASSIGNMENT
# ==========================================
prob = LpProblem("Syndicate_Apex", LpMaximize)
player_vars = {row['player_id']: LpVariable(f"p_{row['player_id']}", cat="Binary") for _, row in df.iterrows()}

prob += lpSum(row['projected_points'] * player_vars[row['player_id']] for _, row in df.iterrows())
prob += lpSum(player_vars[pid] for pid in player_vars) == 11
prob += lpSum(df[df['player_id'] == pid]['credits'].values[0] * player_vars[pid] for pid in player_vars) <= 100.0

for t in df['team'].unique():
    t_pids = df[df['team'] == t]['player_id'].tolist()
    prob += lpSum(player_vars[pid] for pid in t_pids) <= 7
    prob += lpSum(player_vars[pid] for pid in t_pids) >= 1

role_limits = {'wk': (1, 4), 'bat': (1, 6), 'ar': (5, 6), 'bowl': (1, 6)}
for r, (min_lim, max_lim) in role_limits.items():
    r_pids = df[df['role'] == r]['player_id'].tolist()
    if r_pids:
        prob += lpSum(player_vars[pid] for pid in r_pids) >= min_lim
        prob += lpSum(player_vars[pid] for pid in r_pids) <= max_lim

prob.solve(PULP_CBC_CMD(msg=False))

selected_pids = [pid for pid in player_vars if player_vars[pid].value() is not None and player_vars[pid].value() > 0.5]
optimal_pool = df[df['player_id'].isin(selected_pids)].copy()
optimal_pool = optimal_pool.sort_values(by='projected_points', ascending=False).reset_index(drop=True)

# Build Team 1 (Primary EV Multipliers: Rank 1 & Rank 2)
team_1 = optimal_pool.copy()
t1_labels, t1_ev = [], []
for idx, row in team_1.iterrows():
    if idx == 0:
        t1_labels.append('C')
        t1_ev.append(row['projected_points'] * 2.0)
    elif idx == 1:
        t1_labels.append('VC')
        t1_ev.append(row['projected_points'] * 1.5)
    else:
        t1_labels.append('')
        t1_ev.append(row['projected_points'])
team_1['Multiplier'] = t1_labels
team_1['Final_EV'] = t1_ev

# Build Team 2 (Pivot Multipliers: Rank 2 as C, Rank 3 as VC)
team_2 = optimal_pool.copy()
t2_labels, t2_ev = [], []
for idx, row in team_2.iterrows():
    if idx == 1:
        t2_labels.append('C')
        t2_ev.append(row['projected_points'] * 2.0)
    elif idx == 2:
        t2_labels.append('VC')
        t2_ev.append(row['projected_points'] * 1.5)
    else:
        t2_labels.append('')
        t2_ev.append(row['projected_points'])
team_2['Multiplier'] = t2_labels
team_2['Final_EV'] = t2_ev

# ==========================================
# 6. TERMINAL OUTPUT & DUAL CSV EXPORT
# ==========================================
os.makedirs(OUTPUT_DIR, exist_ok=True)
team_1.to_csv(os.path.join(OUTPUT_DIR, "Team_1_Primary.csv"), index=False)
team_2.to_csv(os.path.join(OUTPUT_DIR, "Team_2_Pivot.csv"), index=False)

print("=======================================================")
print(f"   TEAM 1 (PRIMARY) - FOR ₹50 H2H & ₹19 GPP            ")
print(f"   Total Projected EV: {team_1['Final_EV'].sum():.1f} | Credits: {team_1['credits'].sum():.1f}/100")
print("=======================================================")
print(team_1[['Multiplier', 'name', 'team', 'role', 'credits', 'projected_points', 'Final_EV']].to_string(index=False))

print("\n=======================================================")
print(f"   TEAM 2 (PIVOT) - FOR ₹5 GPP LOTTO ENTRY             ")
print(f"   Total Projected EV: {team_2['Final_EV'].sum():.1f} | Credits: {team_2['credits'].sum():.1f}/100")
print("=======================================================")
print(team_2[['Multiplier', 'name', 'team', 'role', 'credits', 'projected_points', 'Final_EV']].to_string(index=False))
print("=======================================================\n")
print(f"📁 Both lineups successfully written to: {OUTPUT_DIR}")

# Render Interactive Dashboard for Team 1
fig = px.bar(
    team_1.sort_values(by='Final_EV', ascending=True),
    x='Final_EV',
    y='name',
    color='role',
    orientation='h',
    title=f"Dual Apex 1000+ Primary XI ({ACTIVE_VENUE})",
    hover_data=['team', 'credits', 'Multiplier', 'projected_points'],
    color_discrete_map={'ar': '#a855f7', 'bowl': '#10b981', 'bat': '#3b82f6', 'wk': '#ef4444'}
)
fig.update_layout(template="plotly_dark", xaxis_title="Ceiling EV", yaxis_title="Player Name")
html_path = os.path.join(OUTPUT_DIR, "grand_league_dashboard.html")
fig.write_html(html_path, auto_open=False)
webbrowser.open(f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}")
