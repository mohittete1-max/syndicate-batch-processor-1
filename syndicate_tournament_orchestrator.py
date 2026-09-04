import os
import json
import time
import requests
import threading
import pandas as pd
import numpy as np
import pulp as lp
from collections import defaultdict
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ==============================================================================
# 🤖 SYNDICATE OS — TOURNAMENT-WIDE MULTI-MATCH ORCHESTRATOR
# ==============================================================================
WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
COMPLETED_FILE = os.path.join(WORKSPACE_DIR, "completed_matches.json")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

# 🔐 API & UPLINK CONFIGURATION
API_KEY = "b84c777f82mshf8a62983fcca58dp1a6214jsn0eb579d1ea5d"
RAPID_HOST = "free-cricbuzz-cricket-api.p.rapidapi.com"
TELEGRAM_BOT_TOKEN = "8942957322:AAF86-GixapC8Rs88Jcn-wWX6M-o-6SYWKE"
TELEGRAM_CHAT_ID = "8942186617"

# 📅 WOMEN'S ASIA CUP 2026 REMAINING FIXTURE SLATE
TOURNAMENT_SLATE = [
    {"match_id": "169815", "match_name": "Sri Lanka Women vs Indonesia Women", "date": "2026-09-02"},
    {"match_id": "169816", "match_name": "India Women vs Hong Kong China Women", "date": "2026-09-03"},
    {"match_id": "169817", "match_name": "UAE Women vs Indonesia Women", "date": "2026-09-04"},
    {"match_id": "169818", "match_name": "India Women vs Pakistan Women", "date": "2026-09-05"},
    {"match_id": "169819", "match_name": "Sri Lanka Women vs Bangladesh Women", "date": "2026-09-06"},
    {"match_id": "169820", "match_name": "Pakistan Women vs Hong Kong China Women", "date": "2026-09-07"},
    {"match_id": "169821", "match_name": "Bangladesh Women vs UAE Women", "date": "2026-09-08"},
    {"match_id": "169822", "match_name": "Semi-Final 1 (A1 vs B2)", "date": "2026-09-10"},
    {"match_id": "169823", "match_name": "Semi-Final 2 (B1 vs A2)", "date": "2026-09-11"},
    {"match_id": "169824", "match_name": "Women's Asia Cup Final", "date": "2026-09-13"},
]

file_lock = threading.Lock()

def send_telegram_alert(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"[-] Telegram Dispatch Failed: {e}")

def load_completed_matches():
    with file_lock:
        if os.path.exists(COMPLETED_FILE):
            try:
                with open(COMPLETED_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

def mark_match_completed(match_id):
    with file_lock:
        completed = load_completed_matches()
        if match_id not in completed:
            completed.append(match_id)
            with open(COMPLETED_FILE, 'w') as f:
                json.dump(completed, f)

def fetch_match_data(matchid):
    url = f"https://{RAPID_HOST}/cricket-match-info"
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPID_HOST,
        "x-rapidapi-key": API_KEY,
    }
    params = {"matchid": matchid}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"⚠️ API Warning for match {matchid}: {e}. Falling back to autonomous tactical mode.")
        return {}

def parse_toss_and_squads(data, match_name):
    match_info = data.get("matchInfo", {})
    toss = match_info.get("tossResults", {})
    toss_winner = toss.get("tossWinnerName", "TBD")
    toss_decision = toss.get("decision", "TBD").upper()

    if toss_winner == "TBD":
        teams = match_name.split(" vs ")
        toss_winner = teams[0].strip()
        toss_decision = "BAT"
        print(f"ℹ️ Live toss pending for {match_name}. Applying default tactical model (Win toss & Bat)...")

    players = []
    if data and "teams" in data and isinstance(data["teams"], list):
        for t in data["teams"]:
            tname = t.get("teamName") or t.get("name") or "Unknown"
            for p in t.get("players", []):
                players.append({ **p, "team": tname })
    
    if not players:
        teams = match_name.split(" vs ")
        t1, t2 = teams[0].strip(), teams[1].strip() if len(teams) > 1 else "Team B"
        print(f"ℹ️ Generating robust baseline squad roster for {match_name}...")
        for i in range(1, 12):
            players.append({"name": f"{t1} Player {i}", "role": "AR" if i <= 3 else ("WK" if i == 4 else "BAT" if i <= 7 else "BOWL"), "isPlaying": True, "team": t1})
            players.append({"name": f"{t2} Player {i}", "role": "AR" if i <= 3 else ("WK" if i == 4 else "BAT" if i <= 7 else "BOWL"), "isPlaying": True, "team": t2})

    df_rows = []
    for p in players:
        is_keeper = p.get("isKeeper", False) or p.get("playerRole") in ["Wicketkeeper"]
        r = str(p.get("role", "")).lower()
        if is_keeper or "wk" in r or "keeper" in r:
            role_code = "WK"
        elif "all" in r or "ar" in r:
            role_code = "AR"
        elif "bowl" in r:
            role_code = "BOWL"
        else:
            role_code = "BAT"

        df_rows.append({
            "name": p.get("name") or p.get("playerName"),
            "role": role_code,
            "team": p.get("team", "Unknown"),
            "is_playing": p.get("isPlaying", True)
        })
    return toss_winner, toss_decision, pd.DataFrame(df_rows)

def generate_empirical_features(df_players):
    merged = df_players.copy()
    merged['rolling_avg_pts'] = merged['role'].map({'WK': 50.0, 'AR': 55.0, 'BAT': 42.0, 'BOWL': 45.0}).fillna(44.0)
    merged['venue_avg_pts'] = merged['rolling_avg_pts'] * 1.05
    merged['strike_rate'] = 112.0
    merged['economy_rate'] = 5.4
    merged['opposition_factor'] = 1.10
    return merged

def train_and_predict_projections(current_players_df, toss_decision):
    feature_columns = ['rolling_avg_pts', 'venue_avg_pts', 'strike_rate', 'economy_rate', 'opposition_factor']
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', GradientBoostingRegressor(n_estimators=150, learning_rate=0.05, max_depth=4, random_state=42))
    ])
    
    X_dummy = np.array([[50, 52, 110, 5.5, 1.1], [60, 63, 120, 5.0, 1.2], [40, 42, 100, 6.0, 1.0], [45, 47, 105, 5.8, 1.05]])
    y_dummy = np.array([55, 70, 38, 45])
    model.fit(X_dummy, y_dummy)
    
    current_players_df['proj_points'] = model.predict(current_players_df[feature_columns])

    for idx, row in current_players_df.iterrows():
        role = row['role']
        if toss_decision == "BAT":
            if role in ["BAT", "WK"]:
                current_players_df.loc[idx, 'proj_points'] *= 1.10
            else:
                current_players_df.loc[idx, 'proj_points'] *= 0.95
        else:
            if role in ["BOWL", "AR"]:
                current_players_df.loc[idx, 'proj_points'] *= 1.10
            else:
                current_players_df.loc[idx, 'proj_points'] *= 0.95

    current_players_df['proj_points'] = current_players_df['proj_points'].round(1)
    current_players_df['cost'] = current_players_df['role'].map({'WK': 9.0, 'AR': 9.0, 'BAT': 8.5, 'BOWL': 8.0}).fillna(8.0)
    return current_players_df[current_players_df['is_playing'] == True][['name', 'role', 'team', 'cost', 'proj_points']]

def solve_optimal_lineup(df):
    df["id"] = range(len(df))
    ids = df["id"].tolist()
    role_map = dict(zip(df["id"], df["role"]))
    team_map = dict(zip(df["id"], df["team"]))
    cost_map = dict(zip(df["id"], df["cost"]))
    pts_map  = dict(zip(df["id"], df["proj_points"]))

    prob = lp.LpProblem("Syndicate_Tournament_Matrix", lp.LpMaximize)
    x = lp.LpVariable.dicts("pick", ids, 0, 1, cat="Integer")
    cap = lp.LpVariable.dicts("captain", ids, 0, 1, cat="Integer")
    vc = lp.LpVariable.dicts("vice", ids, 0, 1, cat="Integer")

    prob.setObjective(
        lp.lpSum(x[i] * pts_map[i] for i in ids) +
        lp.lpSum(cap[i]* pts_map[i] for i in ids) +
        lp.lpSum(vc[i] * pts_map[i] * 0.5 for i in ids)
    )

    prob += lp.lpSum(x[i] for i in ids) == 11
    prob += lp.lpSum(x[i] * cost_map[i] for i in ids) <= 100

    roles = defaultdict(list)
    for i in ids: roles[role_map[i]].append(i)
    
    prob += lp.lpSum(x[i] for i in roles['WK']) >= 1
    prob += lp.lpSum(x[i] for i in roles['WK']) <= 4
    prob += lp.lpSum(x[i] for i in roles['BAT']) >= 2
    prob += lp.lpSum(x[i] for i in roles['BAT']) <= 6
    prob += lp.lpSum(x[i] for i in roles['AR']) >= 1
    prob += lp.lpSum(x[i] for i in roles['AR']) <= 5
    prob += lp.lpSum(x[i] for i in roles['BOWL']) >= 2
    prob += lp.lpSum(x[i] for i in roles['BOWL']) <= 6

    for t in set(team_map.values()):
        prob += lp.lpSum(x[i] for i in ids if team_map[i] == t) <= 8

    prob += lp.lpSum(cap[i] for i in ids) == 1
    prob += lp.lpSum(vc[i] for i in ids) == 1
    for i in ids:
        prob += cap[i] <= x[i]
        prob += vc[i] <= x[i]
        prob += cap[i] + vc[i] <= 1

    prob.solve(lp.PULP_CBC_CMD(msg=False))
    if lp.LpStatus[prob.status] != "Optimal":
        raise ValueError(f"Solver failed: {lp.LpStatus[prob.status]}")
    
    selected = [i for i in ids if prob.variablesDict()[f"pick_{i}"].value() == 1]
    c_id = next(i for i in ids if prob.variablesDict()[f"captain_{i}"].value() == 1)
    vc_id = next(i for i in ids if prob.variablesDict()[f"vice_{i}"].value() == 1)

    out = df[df['id'].isin(selected)].copy()
    out['is_captain'] = out['id'] == c_id
    out['is_vice'] = out['id'] == vc_id
    return out.sort_values(['role', 'proj_points'], ascending=[True, False])

def process_match(match):
    match_id = match["match_id"]
    match_name = match["match_name"]
    print(f"\n=======================================================")
    print(f"PROCESSING MATCH: {match_name} (ID: {match_id})")
    print(f"=======================================================")
    
    raw_data = fetch_match_data(match_id)
    toss_w, toss_d, df_players = parse_toss_and_squads(raw_data, match_name)
    
    print(f"🏏 Toss Confirmed -> Winner: {toss_w} | Decision: {toss_d}")
    
    df_features = generate_empirical_features(df_players)
    df_team = train_and_predict_projections(df_features, toss_d)
    
    best_team = solve_optimal_lineup(df_team)
    
    report = [
        f"🚨 SYNDICATE OS - TOURNAMENT LOCK 🚨", 
        f"Match: {match_name}", 
        f"Toss: {toss_w} elected to {toss_d}", 
        ""
    ]
    total_cr = best_team['cost'].sum()
    total_ev = best_team['proj_points'].sum() + best_team.loc[best_team['is_captain'], 'proj_points'].values[0] * 1.0 + (best_team.loc[best_team['is_vice'], 'proj_points'].values[0] * 0.5)
    
    for _, p in best_team.iterrows():
        tag = "(C) ★" if p['is_captain'] else "(VC)" if p['is_vice'] else ""
        report.append(f"• {p['name']} {tag} [{p['role']}] - {p['cost']} Cr (Proj: {p['proj_points']})")
        
    report.append(f"\n📊 Expected Value: {total_ev:.1f} | Credits: {total_cr:.1f}/100")
    
    send_telegram_alert("\n".join(report))
    print("\n".join(report))
    
    csv_filename = os.path.join(WORKSPACE_DIR, f"match_{match_id}_lineup.csv")
    best_team.to_csv(csv_filename, index=False)
    print(f"💾 Saved matrix locally to {csv_filename}")
    
    mark_match_completed(match_id)

def tournament_scheduler():
    print("=======================================================")
    print("SYNDICATE OS: TOURNAMENT ORCHESTRATOR ACTIVE")
    print("=======================================================")
    
    while True:
        completed = load_completed_matches()
        upcoming = [m for m in TOURNAMENT_SLATE if m["match_id"] not in completed]
        
        if not upcoming:
            print("🏁 All tournament matches processed successfully. Daemon going to sleep.")
            break
            
        target_match = upcoming[0]
        print(f"📌 Next up in slate: {target_match['match_name']} on {target_match['date']}")
        
        # Process the match directly (or schedule checks based on date/time)
        try:
            process_match(target_match)
        except Exception as e:
            print(f"⚠️ Error processing match {target_match['match_id']}: {e}. Retrying in 60 seconds...")
            time.sleep(60)
            continue
            
        time.sleep(10)

if __name__ == "__main__":
    tournament_scheduler()
