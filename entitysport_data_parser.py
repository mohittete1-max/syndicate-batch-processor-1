import requests
import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD
import random

# ==========================================
# 1. DATA INGESTION LAYER
# ==========================================
BASE_URL = "https://restapi.entitysport.com/v2"

def fetch_live_match_data(token, match_id):
    print(f"-> Fetching Squad & Toss data for Match ID: {match_id}...")
    squad_url = f"{BASE_URL}/matches/{match_id}/squads/?token={token}"
    info_url = f"{BASE_URL}/matches/{match_id}/info/?token={token}"
    
    squad_response = requests.get(squad_url).json()
    info_response = requests.get(info_url).json()
    return squad_response, info_response

def extract_fantasy_credits(squad_json):
    player_pool = {}
    if squad_json.get('status') == 'error': return player_pool
    response_data = squad_json.get('response', {})
    if not isinstance(response_data, dict): return player_pool
    
    for team_key in ['teama', 'teamb']:
        team_data = response_data.get(team_key, {})
        for player in team_data.get('squads', []):
            player_id = player.get('player_id')
            name = player.get('title') or player.get('name') or player.get('short_name') or 'Unknown'
            raw_credits = str(player.get('fantasy_player_rating', '8.5')).replace(' cr', '').strip()
            try: credits = float(raw_credits)
            except ValueError: credits = 8.5
            if player_id: 
                player_pool[player_id] = {'name': name, 'credits': credits, 'team': team_data.get('name', team_key)}
    return player_pool

def extract_playing_xi(info_json):
    confirmed_xi_ids = []
    if info_json.get('status') == 'error': return confirmed_xi_ids
    response_data = info_json.get('response', {})
    if not isinstance(response_data, dict): return confirmed_xi_ids
    
    for team_key in ['teama', 'teamb']:
        for player in response_data.get(team_key, {}).get('playing_xi', []):
            if player.get('player_id'): confirmed_xi_ids.append(player.get('player_id'))
    return confirmed_xi_ids

def get_clean_dataframe(squad_json, info_json):
    all_players = extract_fantasy_credits(squad_json)
    starting_ids = extract_playing_xi(info_json)
    
    if starting_ids:
        final_dataset = {pid: all_players[pid] for pid in starting_ids if pid in all_players}
    else:
        print("   [!] Playing XI array missing from API. Loading full squad instead.")
        final_dataset = all_players
        
    df = pd.DataFrame.from_dict(final_dataset, orient='index')
    if not df.empty:
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'player_id'}, inplace=True)
    return df


# ==========================================
# 2. LINEUP GENERATOR ENGINE
# ==========================================
def generate_dream11_team(df):
    print("\n--- RUNNING LINEUP OPTIMIZER ---")
    prob = LpProblem("Dream11_Optimization", LpMaximize)
    player_vars = {pid: LpVariable(f"player_{pid}", cat="Binary") for pid in df['player_id']}
    
    # Generate mock roles and points if missing (Will be replaced by your Poisson Core later)
    if 'projected_points' not in df.columns:
        df['projected_points'] = [random.uniform(20, 80) for _ in range(len(df))]
    if 'role' not in df.columns:
        roles = ['wk', 'bat', 'bat', 'bat', 'ar', 'ar', 'bowl', 'bowl', 'bowl', 'bowl']
        df['role'] = [random.choice(roles) for _ in range(len(df))]
        
    # Objective: Maximize Projected Points
    prob += lpSum(df[df['player_id'] == pid]['projected_points'].values[0] * player_vars[pid] for pid in df['player_id'])
    
    # Rule 1: Exactly 11 players
    prob += lpSum(player_vars[pid] for pid in df['player_id']) == 11
    
    # Rule 2: Budget <= 100 Credits
    prob += lpSum(df[df['player_id'] == pid]['credits'].values[0] * player_vars[pid] for pid in df['player_id']) <= 100
    
    # Rule 3: Max 7 players per team
    team_a_name = df['team'].iloc[0]
    team_a_pids = df[df['team'] == team_a_name]['player_id'].tolist()
    prob += lpSum(player_vars[pid] for pid in team_a_pids) <= 7
    prob += lpSum(player_vars[pid] for pid in team_a_pids) >= 4 
    
    # Rule 4: Role Requirements
    wk_pids = df[df['role'] == 'wk']['player_id'].tolist()
    bat_pids = df[df['role'] == 'bat']['player_id'].tolist()
    ar_pids = df[df['role'] == 'ar']['player_id'].tolist()
    bowl_pids = df[df['role'] == 'bowl']['player_id'].tolist()
    
    if wk_pids: prob += lpSum(player_vars[pid] for pid in wk_pids) >= 1
    if bat_pids: prob += lpSum(player_vars[pid] for pid in bat_pids) >= 3
    if ar_pids: prob += lpSum(player_vars[pid] for pid in ar_pids) >= 1
    if bowl_pids: prob += lpSum(player_vars[pid] for pid in bowl_pids) >= 3
    
    print("-> Solving for mathematically perfect team...")
    prob.solve(PULP_CBC_CMD(msg=False))
    
    selected_players = []
    total_cost = 0
    total_proj = 0
    
    for pid in df['player_id']:
        if player_vars[pid].value() == 1.0:
            row = df[df['player_id'] == pid].iloc[0]
            selected_players.append(row)
            total_cost += row['credits']
            total_proj += row['projected_points']
            
    final_team_df = pd.DataFrame(selected_players)
    return final_team_df, total_cost, total_proj


# ==========================================
# 3. EXECUTION MASTER SCRIPT
# ==========================================
if __name__ == "__main__":
    print("==========================================")
    print(" UNIVERSAL CRICKET OPTIMIZER: BOOTING UP  ")
    print("==========================================\n")
    
    DEMO_TOKEN = "ec471071441bb2ac538a0ff901abd249"
    TARGET_MATCH = "87016" 
    
    live_squad, live_info = fetch_live_match_data(DEMO_TOKEN, TARGET_MATCH)
    player_df = get_clean_dataframe(live_squad, live_info)
    
    if player_df.empty:
        print("\n[!] Failed to load players. Exiting optimizer.")
    else:
        print(f"-> Successfully loaded {len(player_df)} verified players.")
        optimal_team, used_credits, ev_points = generate_dream11_team(player_df)
        
        print("\n==========================================")
        print("         FINAL DREAM11 OPTIMAL XI         ")
        print("==========================================")
        print(optimal_team[['name', 'team', 'role', 'credits', 'projected_points']].to_string(index=False))
        print("------------------------------------------")
        print(f"Total Credits Used: {used_credits:.1f} / 100")
        print(f"Projected EV Points: {ev_points:.1f}")
        print("==========================================\n")
