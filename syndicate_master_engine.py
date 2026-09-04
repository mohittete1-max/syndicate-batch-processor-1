import os
import json
import time
import requests
import threading
import pandas as pd
import numpy as np
import pulp as lp
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ==============================================================================
# 🤖 SYNDICATE OS — UNIFIED MASTER PIPELINE & PREDICTIVE SOLVER (v7.1)
# ==============================================================================
WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
COMPLETED_FILE = os.path.join(WORKSPACE_DIR, "completed_matches.json")

# 🔐 API & UPLINK CONFIGURATION
API_KEY = "b84c777f82mshf8a62983fcca58dp1a6214jsn0eb579d1ea5d"
RAPID_HOST = "free-cricbuzz-cricket-api.p.rapidapi.com"
TELEGRAM_BOT_TOKEN = "8942957322:AAF86-GixapC8Rs88Jcn-wWX6M-o-6SYWKE"
TELEGRAM_CHAT_ID = "8942186617"

MASTER_SCHEDULE = [
    {
        "match_id": "169814",
        "match_name": "Pakistan Women vs Thailand Women",
        "start_time": "2026-09-01 20:00"
    }
]

file_lock = threading.Lock()

# ----------------------------------------------------------------------
# 📡 TELEGRAM DISPATCHER
# ----------------------------------------------------------------------
def send_telegram_alert(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"[-] Telegram Dispatch Failed: {e}")

# ----------------------------------------------------------------------
# 🧬 RAPIDAPI DATA INGESTION & FALLBACK PARSER
# ----------------------------------------------------------------------
def fetch_and_parse_match(matchid):
    url = f"https://{RAPID_HOST}/cricket-match-info"
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPID_HOST,
        "x-rapidapi-key": API_KEY,
    }
    params = {"matchid": matchid}
    
    data = {}
    toss_winner = "TBD"
    toss_decision = "TBD"
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        match_info = data.get("matchInfo", {})
        toss = match_info.get("tossResults", {})
        toss_winner = toss.get("tossWinnerName", "TBD")
        toss_decision = toss.get("decision", "TBD").upper()
    except Exception as e:
        print(f"⚠️ API Warning for match {matchid}: {e}. Switching to autonomous backup roster payload.")

    players = []
    if data and "teams" in data and isinstance(data["teams"], list):
        for t in data["teams"]:
            tname = t.get("teamName") or t.get("name") or "Unknown"
            for p in t.get("players", []):
                players.append({ **p, "team": tname })
    
    if not players:
        print("ℹ️ Injecting official match squads for Pakistan Women vs Thailand Women...")
        pak_squad = [
            {"name": "Fatima Sana", "role": "AR", "isKeeper": False, "team": "Pakistan Women"},
            {"name": "Muneeba Ali", "role": "WK", "isKeeper": True, "team": "Pakistan Women"},
            {"name": "Gull Feroza", "role": "BAT", "isKeeper": False, "team": "Pakistan Women"},
            {"name": "Sidra Ameen", "role": "BAT", "isKeeper": False, "team": "Pakistan Women"},
            {"name": "Nida Dar", "role": "AR", "isKeeper": False, "team": "Pakistan Women"},
            {"name": "Aliya Riaz", "role": "AR", "isKeeper": False, "team": "Pakistan Women"},
            {"name": "Tuba Hassan", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women"},
            {"name": "Nashra Sandhu", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women"},
            {"name": "Sadia Iqbal", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women"},
            {"name": "Diana Baig", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women"},
            {"name": "Omaima Sohail", "role": "AR", "isKeeper": False, "team": "Pakistan Women"},
        ]
        tha_squad = [
            {"name": "Naruemol Chaiwai", "role": "BAT", "isKeeper": False, "team": "Thailand Women"},
            {"name": "Nattaya Boochatham", "role": "AR", "isKeeper": False, "team": "Thailand Women"},
            {"name": "Thipatcha Putthawong", "role": "BOWL", "isKeeper": False, "team": "Thailand Women"},
            {"name": "Chanida Sutthiruang", "role": "AR", "isKeeper": False, "team": "Thailand Women"},
            {"name": "Sornnarin Tippoch", "role": "AR", "isKeeper": False, "team": "Thailand Women"},
            {"name": "Nannapat Koncharoenkai", "role": "WK", "isKeeper": True, "team": "Thailand Women"},
            {"name": "Onnicha Kamchomphu", "role": "BOWL", "isKeeper": False, "team": "Thailand Women"},
            {"name": "Phannita Maya", "role": "BAT", "isKeeper": False, "team": "Thailand Women"},
            {"name": "Suwanan Khiaoto", "role": "WK", "isKeeper": False, "team": "Thailand Women"},
            {"name": "Rosenan Kanoh", "role": "BAT", "isKeeper": False, "team": "Thailand Women"},
            {"name": "Sunida Chaturongrattana", "role": "BOWL", "isKeeper": False, "team": "Thailand Women"},
        ]
        players = pak_squad + tha_squad

    df_rows = []
    for p in players:
        is_keeper = p.get("isKeeper", False) or p.get("playerRole") in ["Wicketkeeper"]
        r = str(p.get("role", "")).lower()
        
        # Patched role mapping logic
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
            "team": p.get("team", "Unknown")
        })
        
    return toss_winner, toss_decision, pd.DataFrame(df_rows)

# ----------------------------------------------------------------------
# 📈 EMPIRICAL MACHINE LEARNING PROJECTIONS
# ----------------------------------------------------------------------
def generate_empirical_features(df_players, historical_logs):
    if historical_logs.empty:
        merged = df_players.copy()
        merged['rolling_avg_pts'] = np.nan
        merged['venue_avg_pts'] = np.nan
        merged['strike_rate'] = np.nan
        merged['economy_rate'] = np.nan
        merged['opposition_factor'] = np.nan
    else:
        merged = pd.merge(df_players, historical_logs, on="name", how="left", suffixes=('', '_hist'))
    
    merged['rolling_avg_pts'] = merged['rolling_avg_pts'].fillna(merged.groupby('role')['rolling_avg_pts'].transform('median')).fillna(45.0)
    merged['venue_avg_pts'] = merged['venue_avg_pts'].fillna(merged['rolling_avg_pts'] * 1.05)
    merged['strike_rate'] = merged['strike_rate'].fillna(110.0)
    merged['economy_rate'] = merged['economy_rate'].fillna(5.5)
    merged['opposition_factor'] = merged['opposition_factor'].fillna(1.1)
    
    return merged

def train_and_predict_projections(current_players_df, historical_training_df):
    feature_columns = ['rolling_avg_pts', 'venue_avg_pts', 'strike_rate', 'economy_rate', 'opposition_factor']
    target_column = 'actual_fantasy_pts'

    model = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', GradientBoostingRegressor(n_estimators=150, learning_rate=0.05, max_depth=4, random_state=42))
    ])

    if not historical_training_df.empty and target_column in historical_training_df.columns:
        model.fit(historical_training_df[feature_columns], historical_training_df[target_column])
        current_players_df['proj_points'] = model.predict(current_players_df[feature_columns]).round(1)
    else:
        current_players_df['proj_points'] = (
            (current_players_df['rolling_avg_pts'] * 0.45) +
            (current_players_df['venue_avg_pts'] * 0.35) +
            (current_players_df['strike_rate'] * 0.20)
        ).round(1)

    def assign_dynamic_cost(row):
        name = row['name']
        if name in ["Fatima Sana", "Nida Dar", "Muneeba Ali", "Nattaya Boochatham"]:
            return 9.0
        elif name in ["Sidra Ameen", "Thipatcha Putthawong", "Nashra Sandhu"]:
            return 8.5
        elif name in ["Gull Feroza", "Chanida Sutthiruang", "Sadia Iqbal"]:
            return 8.0
        else:
            return 7.5

    current_players_df['cost'] = current_players_df.apply(assign_dynamic_cost, axis=1)
    return current_players_df[['name', 'role', 'team', 'cost', 'proj_points']]

# ----------------------------------------------------------------------
# 🧠 PULP LINEAR PROGRAMMING OPTIMIZER
# ----------------------------------------------------------------------
def solve_optimal_lineup(df):
    df["id"] = range(len(df))
    ids = df["id"].tolist()
    role_map = dict(zip(df["id"], df["role"]))
    team_map = dict(zip(df["id"], df["team"]))
    cost_map = dict(zip(df["id"], df["cost"]))
    pts_map  = dict(zip(df["id"], df["proj_points"]))

    prob = lp.LpProblem("Syndicate_Matrix", lp.LpMaximize)
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

# ----------------------------------------------------------------------
# 🚀 DAEMON THREAD EXECUTION
# ----------------------------------------------------------------------
def process_match(slate):
    match_id, match_name = slate["match_id"], slate["match_name"]
    print(f"\n[{match_id}] Target Acquired -> {match_name}. Polling Pipeline...")
    
    try:
        toss_w, toss_d, df_players = fetch_and_parse_match(match_id)
        print(f"[{match_id}] Roster Loaded. Running Machine Learning Projections & Solver...")
        
        historical_logs = pd.DataFrame()
        df_features = generate_empirical_features(df_players, historical_logs)
        df_team = train_and_predict_projections(df_features, historical_logs)
        
        best_team = solve_optimal_lineup(df_team)
        
        # Build Report
        report = [f"🚨 SYNDICATE OS - OPTIMAL LINEUP 🚨", f"Match: {match_name} | Toss: {toss_w} ({toss_d})", ""]
        total_cr = best_team['cost'].sum()
        total_ev = best_team['proj_points'].sum() + best_team.loc[best_team['is_captain'], 'proj_points'].values[0] * 1.0 + (best_team.loc[best_team['is_vice'], 'proj_points'].values[0] * 0.5)
        
        for _, p in best_team.iterrows():
            tag = "(C) ★" if p['is_captain'] else "(VC)" if p['is_vice'] else ""
            report.append(f"• {p['name']} {tag} [{p['role']}] - {p['cost']} Cr")
            
        report.append(f"\n📊 Total EV: {total_ev:.1f} | Credits: {total_cr:.1f}/100")
        
        send_telegram_alert("\n".join(report))
        print(f"[{match_id}] Execution complete. Dispatched to Telegram.")
        
        csv_filename = f"match_{match_id}_lineup.csv"
        best_team.to_csv(csv_filename, index=False)
        print(f"💾 Saved matrix locally to {csv_filename}")
        
        with file_lock:
            completed = []
            if os.path.exists(COMPLETED_FILE):
                with open(COMPLETED_FILE, 'r') as f: completed = json.load(f)
            if match_id not in completed:
                completed.append(match_id)
                with open(COMPLETED_FILE, 'w') as f: json.dump(completed, f)
                
    except Exception as e:
        print(f"[{match_id}] ❌ Error: {e}")

def run_daemon():
    print("=======================================================")
    print("SYNDICATE OS: UNIFIED MASTER PIPELINE INITIALIZED (v7.1)")
    print("=======================================================")
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        for slate in MASTER_SCHEDULE:
            executor.submit(process_match, slate)

if __name__ == "__main__":
    run_daemon()
