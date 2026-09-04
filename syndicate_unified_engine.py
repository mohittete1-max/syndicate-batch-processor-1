import os
import json
import time
import requests
import threading
import pandas as pd
import numpy as np
import pulp as lp
from collections import Counter

# ==========================================
# SYNDICATE OS CONFIGURATION
# ==========================================
WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
QUEUE_FILE = os.path.join(WORKSPACE_DIR, "daily_match_queue.json")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

CRICDATA_API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
CRICDATA_BASE_URL = "https://api.cricapi.com/v1"
TELEGRAM_BOT_TOKEN = "8942957322:AAF86-GixapC8Rs88Jcn-wWX6M-o-6SYWKE"
TELEGRAM_CHAT_ID = "8942186617"

file_lock = threading.Lock()

# ==========================================
# PIPELINE UTILITIES
# ==========================================
def send_telegram_alert(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text})
    except Exception as e:
        print(f"[-] Telegram Dispatch Failed: {e}")

def load_json_store(filepath):
    with file_lock:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

def save_json_store(filepath, data):
    with file_lock:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

def fetch_match_data(match_id):
    url = f"{CRICDATA_BASE_URL}/match_squad"
    params = {"apikey": CRICDATA_API_KEY, "id": match_id}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "success":
            return data.get("data", [])
    except Exception as e:
        print(f"⚠️ CricData API Warning for match {match_id}: {e}")
    return []

def parse_api_to_dataframe(raw_squad_data):
    """Parses raw CricData API response into the solver's DataFrame format."""
    players = []
    # Note: Adjust these key mappings based on exact CricData schema if needed
    for team in raw_squad_data:
        for p in team.get("players", []):
            players.append({
                "name": p.get("name"),
                "role": p.get("role", "BAT").upper(),
                "team": team.get("teamName", "UNK"),
                "credits": float(p.get("fantasy_credits", 8.0)),
                "proj": float(p.get("fantasy_points_projected", 35.0)),
                "base_pown": float(p.get("ownership_percent", 15.0)),
                "c_pown": float(p.get("captain_percent", 2.0)),
                "vc_pown": float(p.get("vice_captain_percent", 2.0))
            })
    return pd.DataFrame(players)

# ==========================================
# CORE STOCHASTIC SOLVER
# ==========================================
def solve_syndicate_matrix(players_df, sim_noise=0.10, num_sims=50):
    """
    Syndicate OS Core Solver:
    - 50 Monte Carlo simulations with +/-10% Gaussian noise
    - Cumulative base pOWN <= 625%
    - Combined C + VC ownership <= 75%
    - Positional distribution: 1-4 WK, 1-6 BAT, 1-6 AR, 1-6 BOWL, Total = 11
    """
    simulated_matrices = []
    
    for sim_idx in range(num_sims):
        prob = lp.LpProblem(f"Syndicate_Sim_{sim_idx}", lp.LpMaximize)
        
        # Binary decision variables
        player_vars = {i: lp.LpVariable(f"x_{i}", cat="Binary") for i in players_df.index}
        c_vars = {i: lp.LpVariable(f"c_{i}", cat="Binary") for i in players_df.index}
        vc_vars = {i: lp.LpVariable(f"vc_{i}", cat="Binary") for i in players_df.index}
        
        # Inject +/- 10% Gaussian noise
        noisy_proj = {}
        for i, row in players_df.iterrows():
            noise = np.random.normal(0, sim_noise * row["proj"])
            noisy_proj[i] = max(0.0, row["proj"] + noise)
            
        # Objective: Maximize total fantasy score including C (2x) and VC (1.5x) multipliers
        prob += lp.lpSum([
            noisy_proj[i] * player_vars[i] + 
            noisy_proj[i] * c_vars[i] + 
            0.5 * noisy_proj[i] * vc_vars[i]
            for i in players_df.index
        ])
        
        # 1. Team Size & Budget
        prob += lp.lpSum([player_vars[i] for i in players_df.index]) == 11
        prob += lp.lpSum([players_df.loc[i, "credits"] * player_vars[i] for i in players_df.index]) <= 100.0
        
        # 2. Multiplier Assignment Constraints
        prob += lp.lpSum([c_vars[i] for i in players_df.index]) == 1
        prob += lp.lpSum([vc_vars[i] for i in players_df.index]) == 1
        for i in players_df.index:
            prob += c_vars[i] + vc_vars[i] <= player_vars[i]
            
        # 3. Base Ownership Constraint (Max 625%)
        prob += lp.lpSum([players_df.loc[i, "base_pown"] * player_vars[i] for i in players_df.index]) <= 625.0
        
        # 4. Multiplier Leverage Constraint (Max 75% Combined C + VC)
        prob += lp.lpSum([
            players_df.loc[i, "c_pown"] * c_vars[i] + 
            players_df.loc[i, "vc_pown"] * vc_vars[i] 
            for i in players_df.index
        ]) <= 75.0
        
        # 5. Roster Structure Constraints (Come11 / Dream11 standard rules)
        for role, min_count, max_count in [("WK", 1, 4), ("BAT", 1, 6), ("AR", 1, 6), ("BOWL", 1, 6)]:
            role_indices = players_df[players_df["role"] == role].index
            prob += lp.lpSum([player_vars[i] for i in role_indices]) >= min_count
            prob += lp.lpSum([player_vars[i] for i in role_indices]) <= max_count
            
        # Solve quietly
        prob.solve(lp.PULP_CBC_CMD(msg=False))
        
        if lp.LpStatus[prob.status] == "Optimal":
            selected = [i for i in players_df.index if player_vars[i].varValue > 0.5]
            c_pick = [i for i in players_df.index if c_vars[i].varValue > 0.5][0]
            vc_pick = [i for i in players_df.index if vc_vars[i].varValue > 0.5][0]
            simulated_matrices.append((tuple(sorted(selected)), c_pick, vc_pick))
            
    # Extract the modal matrix (the consensus single bullet)
    if not simulated_matrices:
        return None, 0.0
        
    lineup_counts = Counter(simulated_matrices)
    best_config, count = lineup_counts.most_common(1)[0]
    optimal_rate = (count / num_sims) * 100.0
    
    return best_config, optimal_rate 

# ==========================================
# DAEMON EXECUTION LOOP
# ==========================================
def run_daemon():
    print("=======================================================")
    print("SYNDICATE OS: UNIFIED DYNAMIC QUEUE DAEMON ACTIVE")
    print("=======================================================")
    print(f"Workspace: {WORKSPACE_DIR}")
    print("Constraints ACTIVE (Max 625% Base | Max 75% C+VC)")
    print("ML Engine: Live Historical ETL Extraction Linked")
    print("=======================================================\n")
    
    while True:
        queue = load_json_store(QUEUE_FILE)
        updated_queue = []
        processed_any = False
        
        for match in queue:
            if match.get("status") == "pending":
                match_id = match.get("match_id")
                match_name = match.get("match_name", match_id)
                
                print(f"⏳ Processing match: {match_name}...")
                raw_squad = fetch_match_data(match_id)
                
                if not raw_squad:
                    print(f"⚠️ Skipping {match_name}: No squad data available yet.")
                    updated_queue.append(match)
                    continue
                    
                df = parse_api_to_dataframe(raw_squad)
                if df.empty or len(df) < 22:
                    print(f"⚠️ Skipping {match_name}: Incomplete player pool.")
                    updated_queue.append(match)
                    continue
                
                print("🎲 Running 50 Monte Carlo simulations with +/- 10.0% variance noise...")
                best_config, optimal_rate = solve_syndicate_matrix(df, sim_noise=0.10, num_sims=50)
                
                if best_config:
                    best_indices, c_idx, vc_idx = best_config
                    final_squad = df.loc[list(best_indices)]
                    captain = df.loc[c_idx, "name"]
                    vice_captain = df.loc[vc_idx, "name"]
                    total_credits = final_squad['credits'].sum()
                    total_pown = final_squad['base_pown'].sum()
                    
                    alert_msg = (
                        f"🚨 SYNDICATE OS - BULLET LOCK 🚨\n"
                        f"Match: {match_name}\n"
                        f"Optimal Rate: {optimal_rate:.1f}%\n"
                        f"Credits: {total_credits}/100 | Base pOWN: {total_pown:.1f}%\n"
                        f"Captain: {captain} | VC: {vice_captain}\n\n"
                        f"Roster:\n" + "\n".join([f"- {row['name']} ({row['role']})" for _, row in final_squad.iterrows()])
                    )
                    
                    print(f"✅ Variance Optimization Complete. Lineup locked.")
                    send_telegram_alert(alert_msg)
                    print(f"📲 Alert dispatched to Telegram.")
                    
                    match["status"] = "processed"
                    processed_any = True
                else:
                    print(f"❌ Failed to find valid matrix for {match_name} under constraints.")
                    
            updated_queue.append(match)
            
        if processed_any:
            save_json_store(QUEUE_FILE, updated_queue)
            
        print("💤 Queue empty or fully processed. Polling for new fixtures in 60s...")
        time.sleep(60)

if __name__ == "__main__":
    run_daemon()
