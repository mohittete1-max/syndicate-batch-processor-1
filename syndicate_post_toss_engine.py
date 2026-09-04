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
# 🤖 SYNDICATE OS — UNIFIED POST-TOSS ENGINE & MASTER PIPELINE (v8.0)
# ==============================================================================
WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
COMPLETED_FILE = os.path.join(WORKSPACE_DIR, "completed_matches.json")

# 🔐 API & UPLINK CONFIGURATION
API_KEY = "b84c777f82mshf8a62983fcca58dp1a6214jsn0eb579d1ea5d"
RAPID_HOST = "free-cricbuzz-cricket-api.p.rapidapi.com"
TELEGRAM_BOT_TOKEN = "8942957322:AAF86-GixapC8Rs88Jcn-wWX6M-o-6SYWKE"
TELEGRAM_CHAT_ID = "8942186617"

MATCH_ID = "169814"
MATCH_NAME = "Pakistan Women vs Thailand Women"

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
# 🧬 RAPIDAPI DATA INGESTION & TOSS/XI PARSER
# ----------------------------------------------------------------------
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
        print(f"⚠️ API Warning for match {matchid}: {e}. Switching to autonomous backup roster payload.")
        return {}

def parse_toss_and_squads(data):
    match_info = data.get("matchInfo", {})
    toss = match_info.get("tossResults", {})
    toss_winner = toss.get("tossWinnerName", "TBD")
    toss_decision = toss.get("decision", "TBD").upper()

    players = []
    if data and "teams" in data and isinstance(data["teams"], list):
        for t in data["teams"]:
            tname = t.get("teamName") or t.get("name") or "Unknown"
            for p in t.get("players", []):
                players.append({ **p, "team": tname })
    
    if not players:
        print("ℹ️ Injecting official match squads for Pakistan Women vs Thailand Women...")
        pak_squad = [
            {"name": "Fatima Sana", "role": "AR", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
            {"name": "Muneeba Ali", "role": "WK", "isKeeper": True, "team": "Pakistan Women", "isPlaying": True},
            {"name": "Gull Feroza", "role": "BAT", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
            {"name": "Sidra Ameen", "role": "BAT", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
            {"name": "Nida Dar", "role": "AR", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
            {"name": "Aliya Riaz", "role": "AR", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
            {"name": "Tuba Hassan", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
            {"name": "Nashra Sandhu", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
            {"name": "Sadia Iqbal", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
            {"name": "Diana Baig", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
            {"name": "Omaima Sohail", "role": "AR", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
        ]
        tha_squad = [
            {"name": "Naruemol Chaiwai", "role": "BAT", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
            {"name": "Nattaya Boochatham", "role": "AR", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
            {"name": "Thipatcha Putthawong", "role": "BOWL", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
            {"name": "Chanida Sutthiruang", "role": "AR", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
            {"name": "Sornnarin Tippoch", "role": "AR", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
            {"name": "Nannapat Koncharoenkai", "role": "WK", "isKeeper": True, "team": "Thailand Women", "isPlaying": True},
            {"name": "Onnicha Kamchomphu", "role": "BOWL", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
            {"name": "Phannita Maya", "role": "BAT", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
            {"name": "Suwanan Khiaoto", "role": "WK", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
            {"name": "Rosenan Kanoh", "role": "BAT", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
            {"name": "Sunida Chaturongrattana", "role": "BOWL", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
        ]
        players = pak_squad + tha_squad

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

# ----------------------------------------------------------------------
# 📈 EMPIRICAL MACHINE LEARNING PROJECTIONS & POST-TOSS MULTIPLIERS
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

def train_and_predict_projections(current_players_df, historical_training_df, toss_decision):
    feature_columns = ['rolling_avg_pts', 'venue_avg_pts', 'strike_rate', 'economy_rate', 'opposition_factor']
    target_column = 'actual_fantasy_pts'

    model = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', GradientBoostingRegressor(n_estimators=150, learning_rate=0.05, max_depth=4, random_state=42))
    ])

    if not historical_training_df.empty and target_column in historical_training_df.columns:
        model.fit(historical_training_df[feature_columns], historical_training_df[target_column])
        base_proj = model.predict(current_players_df[feature_columns])
    else:
        base_proj = (
            (current_players_df['rolling_avg_pts'] * 0.45) +
            (current_players_df['venue_avg_pts'] * 0.35) +
            (current_players_df['strike_rate'] * 0.20)
        )

    current_players_df['proj_points'] = base_proj

    # Apply Post-Toss Multipliers based on decision
    for idx, row in current_players_df.iterrows():
        role = row['role']
        if toss_decision == "BAT":
            if role in ["BAT", "WK"]:
                current_players_df.loc[idx, 'proj_points'] *= 1.10
            else:
                current_players_df.loc[idx, 'proj_points'] *= 0.95
        elif toss_decision == "BOWL":
            if role in ["BOWL", "AR"]:
                current_players_df.loc[idx, 'proj_points'] *= 1.10
            else:
                current_players_df.loc[idx, 'proj_points'] *= 0.95

    current_players_df['proj_points'] = current_players_df['proj_points'].round(1)

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
    return current_players_df[current_players_df['is_playing'] == True][['name', 'role', 'team', 'cost', 'proj_points']]

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

    prob = lp.LpProblem("Syndicate_PostToss_Matrix", lp.LpMaximize)
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
# 🚀 POST-TOSS ORCHESTRATOR & POLLING DAEMON
# ----------------------------------------------------------------------
def run_post_toss_engine():
    print("=======================================================")
    print("SYNDICATE OS: POST-TOSS ENGINE ACTIVE (Match 169814)")
    print("=======================================================")
    
    while True:
        try:
            print(f"[{MATCH_ID}] Polling for Toss & Playing XIs...")
            raw_data = fetch_match_data(MATCH_ID)
            toss_w, toss_d, df_players = parse_toss_and_squads(raw_data)
            
            if toss_w != "TBD" and toss_d != "TBD":
                print(f"🏏 Toss Confirmed: {toss_w} won, chose to {toss_d}!")
                
                historical_logs = pd.DataFrame()
                df_features = generate_empirical_features(df_players, historical_logs)
                df_team = train_and_predict_projections(df_features, historical_logs, toss_d)
                
                best_team = solve_optimal_lineup(df_team)
                
                # Build Report
                report = [
                    f"🚨 SYNDICATE OS - POST-TOSS LINEUP LOCK 🚨", 
                    f"Match: {MATCH_NAME}", 
                    f"Toss: {toss_w} elected to {toss_d}", 
                    ""
                ]
                total_cr = best_team['cost'].sum()
                total_ev = best_team['proj_points'].sum() + best_team.loc[best_team['is_captain'], 'proj_points'].values[0] * 1.0 + (best_team.loc[best_team['is_vice'], 'proj_points'].values[0] * 0.5)
                
                for _, p in best_team.iterrows():
                    tag = "(C) ★" if p['is_captain'] else "(VC)" if p['is_vice'] else ""
                    report.append(f"• {p['name']} {tag} [{p['role']}] - {p['cost']} Cr")
                    
                report.append(f"\n📊 Post-Toss EV: {total_ev:.1f} | Credits: {total_cr:.1f}/100")
                
                send_telegram_alert("\n".join(report))
                print("✅ Post-Toss Optimal Lineup locked and dispatched to Telegram!")
                
                csv_filename = f"match_{MATCH_ID}_post_toss_lineup.csv"
                best_team.to_csv(csv_filename, index=False)
                print(f"💾 Saved matrix locally to {csv_filename}")
                
                with file_lock:
                    completed = []
                    if os.path.exists(COMPLETED_FILE):
                        with open(COMPLETED_FILE, 'r') as f: completed = json.load(f)
                    if MATCH_ID not in completed:
                        completed.append(MATCH_ID)
                        with open(COMPLETED_FILE, 'w') as f: json.dump(completed, f)
                break
            else:
                print("⏳ Toss yet to take place or API payload pending. Retrying in 30 seconds...")
                time.sleep(30)
                
        except Exception as e:
            print(f"⚠️ Polling exception: {e}. Retrying in 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    run_post_toss_engine()
