import os
import requests
import pandas as pd
import numpy as np
import pulp as lp
from collections import Counter
import plotly.express as px

# ==========================================
# SYSTEM CONFIGURATION
# ==========================================
WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
os.makedirs(WORKSPACE_DIR, exist_ok=True)

TELEGRAM_BOT_TOKEN = "8942957322:AAF86-GixapC8Rs88Jcn-wWX6M-o-6SYWKE"
TELEGRAM_CHAT_ID = "8942186617"

# ==========================================
# AUTONOMOUS MATCH CLASSIFICATION ENGINE
# ==========================================
TIER_1_TEAMS = {
    "IND", "AUS", "ENG", "SA", "NZ", "PAK", "SL", "WI", "BAN", "AFG", "IRE", "ZIM", "NAM",
    "INDW", "AUSW", "ENGW", "SAW", "NZW", "PAKW", "SLW", "WIW", "BANW", "IREW", "ZIMW"
}

def determine_match_topology(players_df):
    """Scans the dataframe to autonomously assign the Match Tier."""
    unique_teams = players_df['team'].unique().tolist()
    if len(unique_teams) != 2:
        return "T1_v_T1"
        
    normalized = [t.strip().upper().replace("-", "").replace("_", "") for t in unique_teams]
    t1_count = sum(1 for team in normalized if team in TIER_1_TEAMS)
    
    if t1_count == 1:
        return "T1_v_T2" # Asymmetric Blowout / Mismatch
    return "T1_v_T1"     # Competitive/Symmetric

# ==========================================
# DISPATCH, EXPORT & VISUALIZATION UTILITIES
# ==========================================
def send_telegram_alert(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
        if resp.status_code == 200:
            print("📲 Alert dispatched to Telegram.")
    except Exception as e:
        print(f"[-] Telegram Dispatch Error: {e}")

def export_to_csv(final_squad, captain, vice_captain, match_name):
    filename = f"{match_name.replace(' ', '_').replace('-', '_')}_Lineup.csv"
    filepath = os.path.join(WORKSPACE_DIR, filename)
    
    role_order = {"WK": 1, "BAT": 2, "AR": 3, "BOWL": 4}
    sorted_squad = final_squad.copy()
    sorted_squad['role_rank'] = sorted_squad['role'].map(role_order)
    sorted_squad = sorted_squad.sort_values('role_rank')
    
    player_names = sorted_squad['name'].tolist()
    row_data = player_names + [captain, vice_captain]
    columns = [f"Player_{i+1}" for i in range(11)] + ["Captain", "Vice_Captain"]
    
    pd.DataFrame([row_data], columns=columns).to_csv(filepath, index=False)
    print(f"📁 CSV Exported for Bulk Upload: {filename}")

def plot_and_save_leverage(df, match_name):
    filename = f"leverage_matrix_{match_name.replace(' ', '_').replace('-', '_')}.html"
    filepath = os.path.join(WORKSPACE_DIR, filename)
    
    fig = px.scatter(
        df, 
        x="base_pown", 
        y="optimal_pct", 
        color="leverage",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        hover_name="name",
        hover_data={"role": True, "credits": True, "proj": True, "leverage": ":.1f", "base_pown": ":.1f", "optimal_pct": ":.1f"},
        title=f"Syndicate OS Feedback-Calibrated Leverage Distribution: {match_name}",
        labels={"base_pown": "Public pOWN% (Field Expectation)", "optimal_pct": "Optimal % (Engine Reality)"},
        template="plotly_dark"
    )
    
    max_val = max(df["base_pown"].max(), df["optimal_pct"].max()) + 5
    fig.add_shape(
        type="line", line=dict(dash="dash", color="white", width=1),
        x0=0, y0=0, x1=max_val, y1=max_val
    )
    
    fig.add_annotation(x=max_val*0.1, y=max_val*0.9, text="🔥 Core Tournament Value", showarrow=False, font=dict(color="green"))
    fig.add_annotation(x=max_val*0.9, y=max_val*0.1, text="⚠️ Over-Owned Traps (Faded by Feedback Loop)", showarrow=False, font=dict(color="red"))
    
    fig.update_layout(height=700, width=1000)
    fig.write_html(filepath)
    print(f"📊 Saved interactive feedback-calibrated visualization: {filename}")

# ==========================================
# TRIPLE-HEADER MATCH POOLS (Calibrated with Post-Match Insights)
# ==========================================
ENG_IRE_POOL = [
    {"name": "A Hunter", "role": "WK", "team": "IRE-W", "credits": 7.5, "points": 94},
    {"name": "K Chathli", "role": "WK", "team": "ENG-W", "credits": 6.5, "points": 0},
    {"name": "M Bouchier", "role": "BAT", "team": "ENG-W", "credits": 6.0, "points": 356}, # Calibrated post-match surge
    {"name": "S Dunkley", "role": "BAT", "team": "ENG-W", "credits": 8.0, "points": 208}, # Calibrated post-match surge
    {"name": "G Lewis", "role": "BAT", "team": "IRE-W", "credits": 8.5, "points": 113},
    {"name": "R Stokell", "role": "BAT", "team": "IRE-W", "credits": 7.5, "points": 96},
    {"name": "A Capsey", "role": "BAT", "team": "ENG-W", "credits": 8.0, "points": 81},
    {"name": "C Dean", "role": "AR", "team": "ENG-W", "credits": 7.0, "points": 113},
    {"name": "F Kemp", "role": "AR", "team": "ENG-W", "credits": 7.5, "points": 78},
    {"name": "O Prendergast", "role": "AR", "team": "IRE-W", "credits": 9.0, "points": 75},
    {"name": "M Villiers", "role": "AR", "team": "ENG-W", "credits": 6.0, "points": 55},
    {"name": "C Murray", "role": "BOWL", "team": "IRE-W", "credits": 8.0, "points": 130},
    {"name": "I Wong", "role": "BOWL", "team": "ENG-W", "credits": 6.5, "points": 104},
    {"name": "L Filer", "role": "BOWL", "team": "ENG-W", "credits": 6.0, "points": 45},
    {"name": "T Corteen-Coleman", "role": "BOWL", "team": "ENG-W", "credits": 8.0, "points": 20}
]

NAM_ZIM_POOL = [
    {"name": "Z Green", "role": "WK", "team": "NAM", "credits": 6.0, "points": 125},
    {"name": "T Marumani", "role": "WK", "team": "ZIM", "credits": 7.5, "points": 118},
    {"name": "B Curran", "role": "BAT", "team": "ZIM", "credits": 6.0, "points": 164},
    {"name": "A Volschenk", "role": "BAT", "team": "NAM", "credits": 8.0, "points": 139},
    {"name": "L Steenkamp", "role": "BAT", "team": "NAM", "credits": 7.5, "points": 89},
    {"name": "I Kaia", "role": "BAT", "team": "ZIM", "credits": 7.5, "points": 52},
    {"name": "B Evans", "role": "AR", "team": "ZIM", "credits": 7.5, "points": 368}, # Calibrated explosion vector
    {"name": "B Bennett", "role": "AR", "team": "ZIM", "credits": 7.5, "points": 220},
    {"name": "G Erasmus", "role": "AR", "team": "NAM", "credits": 8.0, "points": 204},
    {"name": "J Frylinck", "role": "AR", "team": "NAM", "credits": 7.0, "points": 182},
    {"name": "S Raza", "role": "AR", "team": "ZIM", "credits": 9.0, "points": 165},
    {"name": "R Trumpelmann", "role": "BOWL", "team": "NAM", "credits": 6.0, "points": 223}, # Calibrated upset pacer
    {"name": "N Nyamhuri", "role": "BOWL", "team": "ZIM", "credits": 8.0, "points": 130},
    {"name": "M Heingo", "role": "BOWL", "team": "NAM", "credits": 6.5, "points": 97},
    {"name": "B Muzarabani", "role": "BOWL", "team": "ZIM", "credits": 8.5, "points": 82}
]

IND_HK_POOL = [
    {"name": "Y Daswani", "role": "WK", "team": "HK-W", "credits": 7.0, "points": 58},
    {"name": "R Ghosh", "role": "WK", "team": "IND-W", "credits": 8.0, "points": 18},
    {"name": "S Mandhana", "role": "BAT", "team": "IND-W", "credits": 8.5, "points": 65},
    {"name": "P Rawal", "role": "BAT", "team": "IND-W", "credits": 7.5, "points": 48},
    {"name": "B Fulmali", "role": "BAT", "team": "IND-W", "credits": 8.0, "points": 25},
    {"name": "M Lamplough", "role": "AR", "team": "HK-W", "credits": 6.5, "points": 233},
    {"name": "S Verma", "role": "AR", "team": "IND-W", "credits": 9.0, "points": 280}, # Calibrated blowout captain anchor
    {"name": "K Chan", "role": "AR", "team": "HK-W", "credits": 8.0, "points": 140},
    {"name": "D Sharma", "role": "AR", "team": "IND-W", "credits": 8.5, "points": 134},
    {"name": "M Bibi", "role": "AR", "team": "HK-W", "credits": 6.0, "points": 25},
    {"name": "N Sharma", "role": "BOWL", "team": "IND-W", "credits": 6.5, "points": 126},
    {"name": "A Siu", "role": "BOWL", "team": "HK-W", "credits": 9.0, "points": 106},
    {"name": "S Charani", "role": "BOWL", "team": "IND-W", "credits": 8.0, "points": 95},
    {"name": "K Gaud", "role": "BOWL", "team": "IND-W", "credits": 6.5, "points": 82},
    {"name": "P Rawat", "role": "BOWL", "team": "IND-W", "credits": 8.0, "points": 47}
]

# ==========================================
# PREPARATION & SOLVER (With Feedback Loop Overrides)
# ==========================================
def prepare_data(pool):
    df = pd.DataFrame(pool)
    df = df.rename(columns={"points": "proj"})
    max_proj = df["proj"].max()
    df["base_pown"] = (df["proj"] / max_proj) * 85.0
    df["c_pown"] = (df["proj"] / max_proj) * 20.0
    df["vc_pown"] = (df["proj"] / max_proj) * 15.0
    return df

def solve_syndicate_matrix(players_df, match_tier="T1_v_T1", is_bowling_deck=False, sim_noise=0.15, num_sims=200):
    """
    Simulations updated with feedback-calibrated noise (0.15) to capture 
    associate volatility and lower-order exploding all-rounders.
    """
    simulated_matrices = []
    player_optimal_counts = {i: 0 for i in players_df.index}
    top_proj_idx = players_df['proj'].idxmax()
    
    # Feedback-Calibrated Context Logic
    multiplier_cap = 140.0 if match_tier == "T1_v_T2" else 75.0
    anchor_alpha = True if match_tier == "T1_v_T2" else False
    
    # Blowout Suppression: Restrict middle-order bloat on T1 v T2 mismatches
    max_batters = 3 if match_tier == "T1_v_T2" else (4 if is_bowling_deck else 6)
    min_bowlers = 4 if match_tier == "T1_v_T2" else (3 if is_bowling_deck else 2)

    for sim_idx in range(num_sims):
        prob = lp.LpProblem(f"Sim_{sim_idx}", lp.LpMaximize)
        
        p_vars = {i: lp.LpVariable(f"x_{i}", cat="Binary") for i in players_df.index}
        c_vars = {i: lp.LpVariable(f"c_{i}", cat="Binary") for i in players_df.index}
        vc_vars = {i: lp.LpVariable(f"vc_{i}", cat="Binary") for i in players_df.index}
        
        noisy_proj = {i: max(0.0, row["proj"] + np.random.normal(0, sim_noise * row["proj"])) for i, row in players_df.iterrows()}
            
        # Objective: Full DFS point scaling including C and VC multipliers
        prob += lp.lpSum([noisy_proj[i] * p_vars[i] + noisy_proj[i] * c_vars[i] + 0.5 * noisy_proj[i] * vc_vars[i] for i in players_df.index])
        
        # Core Constraints
        prob += lp.lpSum([p_vars[i] for i in players_df.index]) == 11
        prob += lp.lpSum([players_df.loc[i, "credits"] * p_vars[i] for i in players_df.index]) <= 100.0
        prob += lp.lpSum([players_df.loc[i, "base_pown"] * p_vars[i] for i in players_df.index]) <= 625.0
        
        prob += lp.lpSum([c_vars[i] for i in players_df.index]) == 1
        prob += lp.lpSum([vc_vars[i] for i in players_df.index]) == 1
        for i in players_df.index: 
            prob += c_vars[i] + vc_vars[i] <= p_vars[i]
            
        # Typology Constraint Overrides (Feedback Loop Enforced)
        prob += lp.lpSum([players_df.loc[i, "c_pown"] * c_vars[i] + players_df.loc[i, "vc_pown"] * vc_vars[i] for i in players_df.index]) <= multiplier_cap
        if anchor_alpha: 
            prob += c_vars[top_proj_idx] == 1
            
        # Pitch & Blowout Constraint Overrides
        for role, min_count, max_count in [("WK", 1, 4), ("BAT", 1, max_batters), ("AR", 1, 6), ("BOWL", min_bowlers, 6)]:
            role_indices = players_df[players_df["role"] == role].index
            prob += lp.lpSum([p_vars[i] for i in role_indices]) >= min_count
            prob += lp.lpSum([p_vars[i] for i in role_indices]) <= max_count
            
        prob.solve(lp.PULP_CBC_CMD(msg=False))
        if lp.LpStatus[prob.status] == "Optimal":
            selected = [i for i in players_df.index if p_vars[i].varValue > 0.5]
            
            for i in selected:
                player_optimal_counts[i] += 1
                
            simulated_matrices.append((
                tuple(sorted(selected)), 
                [i for i in players_df.index if c_vars[i].varValue > 0.5][0], 
                [i for i in players_df.index if vc_vars[i].varValue > 0.5][0]
            ))
            
    players_df["optimal_pct"] = [(player_optimal_counts[i] / num_sims) * 100 for i in players_df.index]
    players_df["leverage"] = players_df["optimal_pct"] - players_df["base_pown"]
    
    if not simulated_matrices: 
        return None, 0.0, None, None, players_df
        
    best_config, count = Counter(simulated_matrices).most_common(1)[0]
    return best_config[0], (count / num_sims) * 100.0, best_config[1], best_config[2], players_df

# ==========================================
# EXECUTION ROUTINE
# ==========================================
if __name__ == "__main__":
    matches = {
        "ENG-W vs IRE-W": (ENG_IRE_POOL, False),
        "NAM vs ZIM": (NAM_ZIM_POOL, True),      
        "IND-W vs HK-W": (IND_HK_POOL, False)
    }
    
    for match_name, (pool, is_bowl_deck) in matches.items():
        print(f"\n=======================================================")
        print(f"🏏 PROCESSING SLATE: {match_name}")
        
        df = prepare_data(pool)
        calculated_tier = determine_match_topology(df)
        print(f"🧠 Autonomous Topology (Feedback Adjusted): {calculated_tier} | Bowling Deck: {is_bowl_deck}")
        print(f"⚙️ Running 200 Monte Carlo simulations with calibrated variance...")
        
        best_indices, rate, c_idx, vc_idx, leveraged_df = solve_syndicate_matrix(
            df, 
            match_tier=calculated_tier, 
            is_bowling_deck=is_bowl_deck,
            sim_noise=0.15,
            num_sims=200
        )
        
        if not best_indices:
            print("⚠️ No valid matrix found under calibrated constraints.")
            continue
            
        final_squad = df.loc[list(best_indices)]
        captain = df.loc[c_idx, "name"]
        vice_captain = df.loc[vc_idx, "name"]
        total_credits = final_squad['credits'].sum()
        total_pown = final_squad['base_pown'].sum()
        
        # Execute unified pipeline exports
        export_to_csv(final_squad, captain, vice_captain, match_name)
        plot_and_save_leverage(leveraged_df, match_name)
        
        # Dispatch Telegram alert
        alert_msg = (
            f"🚨 SYNDICATE OS - FEEDBACK BULLET LOCK 🚨\n"
            f"Match: {match_name}\n"
            f"Topology: {calculated_tier} | Rate: {rate:.1f}%\n"
            f"Credits: {total_credits}/100 | Base pOWN: {total_pown:.1f}%\n"
            f"Captain: {captain} | VC: {vice_captain}\n\n"
            f"Roster:\n" + "\n".join([f"- {row['name']} ({row['role']})" for _, row in final_squad.iterrows()])
        )
        send_telegram_alert(alert_msg)
        
        # Terminal confirmation
        print(f"🏆 BULLET LOCK OPTIMAL (Achieved in {rate:.1f}% of Sims)")
        print(f"Captain (C): {captain} | Vice-Captain (VC): {vice_captain}")
        print(f"Total Credits: {total_credits}/100.0 | Base pOWN: {total_pown:.1f}%")
        print("-" * 65)
        print(f"{'PLAYER':<20} | {'ROLE':<5} | {'CREDITS':<7} | {'PROJ'}")
        print("-" * 65)
        for _, row in final_squad.iterrows():
            marker = " (C)" if row['name'] == captain else (" (VC)" if row['name'] == vice_captain else "")
            print(f"{row['name'] + marker:<20} | {row['role']:<5} | {row['credits']:<7} | {row['proj']}")
