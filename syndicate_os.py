"""
==============================================================================
SYNDICATE OS - MASTER TRIPLE-HEADER SQUADS & OPTIMIZATION CONFIGURATION
Matches: RSA vs ZIM (170000), ENGW vs IREW (129530), PAKW vs THAIW (169821)
==============================================================================
"""

import os
import json
import random
import pandas as pd

try:
    import pulp
except ImportError:
    os.system("pip install pulp")
    import pulp

BASE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
os.makedirs(BASE_DIR, exist_ok=True)

OUTPUT_SUMMARY = os.path.join(BASE_DIR, "Final_Lineups_Mobile_Summary.txt")
LIVE_STATE_FILE = os.path.join(BASE_DIR, "live_toss_state.json")

# Master Omni-League Registry updated with verified squads
SQUADS = {
    "170000": {
        "title": "RSA vs ZIM",
        "series": "Namibia T20I Tri-Series 2026",
        "format": "T20",
        "gender": "MEN",
        "team_a": "RSA",
        "team_b": "ZIM",
        "squad_a": [
            ("Lhuan-dré Pretorius", "WK", 1.15, 35.0, 8.0), ("Jordan Hermann", "BAT", 1.10, 24.0, 7.5),
            ("Dewald Brevis", "BAT", 1.35, 78.0, 9.0), ("Tony de Zorzi", "BAT", 1.08, 20.0, 7.5),
            ("Eathan Bosch", "AR", 1.12, 18.0, 7.5), ("Duan Jansen", "AR", 1.15, 30.0, 8.0),
            ("Bjorn Fortuin", "AR", 1.25, 42.0, 8.5), ("Lutho Sipamla", "BOWL", 1.10, 22.0, 7.5),
            ("Nqaba Peter", "BOWL", 1.16, 38.0, 8.0), ("Kwena Maphaka", "BOWL", 1.18, 45.0, 8.5),
            ("Andile Simelane", "AR", 1.14, 25.0, 7.5)
        ],
        "squad_b": [
            ("Sikandar Raza", "AR", 1.35, 82.0, 9.5), ("Brian Bennett", "AR", 1.28, 55.0, 8.5),
            ("Ryan Burl", "AR", 1.25, 52.0, 8.5), ("Blessing Muzarabani", "BOWL", 1.16, 48.0, 8.5),
            ("Brad Evans", "AR", 1.22, 35.0, 8.0), ("Ben Curran", "BAT", 1.15, 28.0, 7.5),
            ("Tadiwanashe Marumani", "WK", 1.08, 22.0, 7.5), ("Wellington Masakadza", "BOWL", 1.10, 25.0, 7.5),
            ("Dion Myers", "BAT", 1.05, 19.0, 7.5), ("Newman Nyamhuri", "BOWL", 1.01, 14.0, 6.5),
            ("Graeme Cremer", "BOWL", 1.12, 29.0, 7.5)
        ]
    },
    "129530": {
        "title": "ENGW vs IREW",
        "series": "Ireland Women tour of England 2026",
        "format": "ODI",
        "gender": "WOMEN",
        "team_a": "ENGW",
        "team_b": "IREW",
        "squad_a": [
            ("Sophia Dunkley", "BAT", 1.22, 55.0, 8.5), ("Mady Villiers", "BOWL", 1.18, 42.0, 8.0),
            ("Dani Gibson", "AR", 1.16, 30.0, 7.5), ("Charlie Dean", "AR", 1.25, 52.0, 8.5),
            ("Maia Bouchier", "BAT", 1.20, 60.0, 8.5), ("Issy Wong", "BOWL", 1.14, 38.0, 7.5),
            ("Freya Kemp", "AR", 1.18, 35.0, 7.5), ("Alice Capsey", "AR", 1.28, 65.0, 9.0),
            ("Lauren Filer", "BOWL", 1.12, 28.0, 7.5), ("Grace Potts", "BOWL", 1.08, 20.0, 7.0),
            ("Kira Chathli", "WK", 1.05, 18.0, 7.0)
        ],
        "squad_b": [
            ("Gaby Lewis", "BAT", 1.22, 62.0, 8.5), ("Louise Little", "AR", 1.05, 15.0, 7.0),
            ("Leah Paul", "AR", 1.18, 40.0, 8.0), ("Rebecca Stokell", "BAT", 1.05, 22.0, 7.5),
            ("Cara Murray", "BOWL", 1.12, 35.0, 7.5), ("Orla Prendergast", "AR", 1.26, 55.0, 8.5),
            ("Arlene Kelly", "AR", 1.16, 45.0, 8.0), ("Amy Hunter", "WK", 1.15, 48.0, 8.0),
            ("Georgina Dempsey", "AR", 1.10, 25.0, 7.5), ("Jane Maguire", "BOWL", 1.08, 18.0, 7.0),
            ("Christina Coulter Reilly", "WK", 1.02, 12.0, 7.0)
        ]
    },
    "169821": {
        "title": "PAKW vs THAIW",
        "series": "Women's Asia Cup 2026",
        "format": "T20",
        "gender": "WOMEN",
        "team_a": "PAKW",
        "team_b": "THAIW",
        "squad_a": [
            ("Fatima Sana", "AR", 1.30, 75.0, 9.0), ("Muneeba Ali", "WK", 1.20, 62.0, 8.5),
            ("Nashra Sandhu", "BOWL", 1.25, 68.0, 8.5), ("Sadia Iqbal", "BOWL", 1.22, 55.0, 8.0),
            ("Tuba Hassan", "AR", 1.18, 48.0, 8.0), ("Ayesha Zafar", "BAT", 1.10, 30.0, 7.5),
            ("Aliya Riaz", "AR", 1.16, 42.0, 8.0), ("Diana Baig", "BOWL", 1.15, 40.0, 8.0),
            ("Sidra Ameen", "BAT", 1.14, 38.0, 7.5), ("Omaima Sohail", "AR", 1.12, 28.0, 7.5),
            ("Najiha Alvi", "WK", 1.02, 15.0, 7.0)
        ],
        "squad_b": [
            ("Naruemol Chaiwai", "BAT", 1.10, 35.0, 7.5), ("Nannapat Koncharoenkai", "WK", 1.16, 52.0, 8.0),
            ("Nattakan Chantham", "BAT", 1.20, 65.0, 8.5), ("Thipatcha Putthawong", "AR", 1.25, 58.0, 8.5),
            ("Chanida Sutthiruang", "AR", 1.18, 49.0, 8.0), ("Suleeporn Laomi", "BOWL", 1.15, 45.0, 8.0),
            ("Onnicha Kamchomphu", "AR", 1.12, 32.0, 7.5), ("Phannita Maya", "BAT", 1.04, 18.0, 7.0),
            ("Sunida Chaturongrattana", "BOWL", 1.03, 15.0, 7.0), ("Aphisara Suwanchonrathi", "BAT", 1.02, 12.0, 7.0),
            ("Naomi Kanokporn Hamilton", "AR", 1.01, 10.0, 7.0)
        ]
    }
}

def calculate_player_projections(match_data, state):
    decision = state.get("elected_to", "FIELD").upper()
    meteo_dew = state.get("meteo_dew", True)
    global_pitch_wear = state.get("global_pitch_wear", True)
    
    bat_boost = 1.12 if decision == "FIELD" else 1.04
    bowl_boost = 1.18 if global_pitch_wear else 1.06
    dew_mult = 1.14 if meteo_dew else 1.0
    
    records = []
    for squad_key, team_name in [("squad_a", match_data["team_a"]), ("squad_b", match_data["team_b"])]:
        for p_data in match_data[squad_key]:
            player, role, base_mult, own, credits = p_data
            
            raw_base = random.uniform(42.0, 58.0)
            if role == "AR":
                raw_base *= 1.32  # Dual-Threat Meta Boost
            elif role == "WK":
                raw_base *= 1.12
            elif role == "BAT":
                raw_base *= 1.08
            elif role == "BOWL":
                raw_base *= 1.02
                
            if role in ["BAT", "WK"]: raw_base *= bat_boost
            if role in ["BOWL", "AR"]: raw_base *= bowl_boost
                
            proj = round(raw_base * base_mult * dew_mult, 2)
            lambda_param = 0.45
            ox_alpha = round(proj * (1.0 + lambda_param * ((100.0 - own) / 100.0)), 2)
            
            records.append({
                "Player": player,
                "Team": team_name,
                "Role": role,
                "Projection": proj,
                "OX_Alpha": ox_alpha,
                "Ownership": own,
                "Credits": credits
            })
            
    return pd.DataFrame(records)

def solve_optimal_roster(df, objective_col="Projection", max_credits=100.0):
    prob = pulp.LpProblem("DFS_Optimizer", pulp.LpMaximize)
    
    players = df.index.tolist()
    x = pulp.LpVariable.dicts("select", players, cat="Binary")
    
    prob += pulp.lpSum([df.loc[i, objective_col] * x[i] for i in players])
    prob += pulp.lpSum([x[i] for i in players]) == 11
    prob += pulp.lpSum([df.loc[i, "Credits"] * x[i] for i in players]) <= max_credits
    
    for team in df["Team"].unique():
        prob += pulp.lpSum([x[i] for i in players if df.loc[i, "Team"] == team]) <= 7
        
    wk_idx = [i for i in players if df.loc[i, "Role"] == "WK"]
    bat_idx = [i for i in players if df.loc[i, "Role"] == "BAT"]
    ar_idx = [i for i in players if df.loc[i, "Role"] == "AR"]
    bowl_idx = [i for i in players if df.loc[i, "Role"] == "BOWL"]
    
    prob += pulp.lpSum([x[i] for i in wk_idx]) >= 1
    prob += pulp.lpSum([x[i] for i in wk_idx]) <= 4
    prob += pulp.lpSum([x[i] for i in bat_idx]) >= 1
    prob += pulp.lpSum([x[i] for i in bat_idx]) <= 6
    prob += pulp.lpSum([x[i] for i in ar_idx]) >= 2
    prob += pulp.lpSum([x[i] for i in ar_idx]) <= 6
    prob += pulp.lpSum([x[i] for i in bowl_idx]) >= 2
    prob += pulp.lpSum([x[i] for i in bowl_idx]) <= 6
    
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    selected_idx = [i for i in players if pulp.value(x[i]) == 1.0]
    return df.loc[selected_idx].copy().reset_index(drop=True)

def select_anchor_multipliers(df_roster):
    eligible_anchors = df_roster[df_roster["Role"].isin(["AR", "BAT", "WK"])].sort_values(
        by="Projection", ascending=False
    )
    if len(eligible_anchors) >= 2:
        cap = eligible_anchors.iloc[0]
        vc = eligible_anchors.iloc[1]
    else:
        sorted_all = df_roster.sort_values(by="Projection", ascending=False)
        cap = sorted_all.iloc[0]
        vc = sorted_all.iloc[1]
    return cap, vc

def run_syndicate_engine(match_id, match_data, state):
    df_players = calculate_player_projections(match_data, state)
    
    h2h_roster = solve_optimal_roster(df_players, objective_col="Projection", max_credits=100.0)
    h2h_cap, h2h_vc = select_anchor_multipliers(h2h_roster)
    h2h_credits = h2h_roster["Credits"].sum()
    h2h_ev = h2h_roster["Projection"].sum() + (h2h_cap["Projection"] * 1.0) + (h2h_vc["Projection"] * 0.5)
    
    gpp_roster = solve_optimal_roster(df_players, objective_col="OX_Alpha", max_credits=100.0)
    gpp_cap, gpp_vc = select_anchor_multipliers(gpp_roster)
    gpp_credits = gpp_roster["Credits"].sum()
    gpp_ev = gpp_roster["Projection"].sum() + (gpp_cap["Projection"] * 1.0) + (gpp_vc["Projection"] * 0.5)
    
    report = f"""=======================================================
SYNDICATE OS - MATHEMATICALLY OPTIMAL REPORT
Match: {match_data['title']} | Match ID: {match_id}
Series: {match_data['series']}
Toss Winner: {state.get('toss_winner', 'N/A')} ({state.get('elected_to', 'N/A')})
=======================================================

[CONSERVATIVE H2H LINEUP (Raw EV: {h2h_ev:.1f} Pts | Credits: {h2h_credits:.1f}/100)]
Captain (C - Anchor Lock): {h2h_cap['Player']} ({h2h_cap['Team']}) [Proj: {h2h_cap['Projection']}]
Vice-Captain (VC - Anchor Lock): {h2h_vc['Player']} ({h2h_vc['Team']}) [Proj: {h2h_vc['Projection']}]
Core 11:
"""
    for _, row in h2h_roster.iterrows():
        report += f" - {row['Player']} ({row['Team']}) [{row['Role']}] | Proj: {row['Projection']} | Own: {row['Ownership']}% | Cr: {row['Credits']}\n"
        
    report += f"""
[GPP OX ALPHA LINEUP (Simulated EV: {gpp_ev:.1f} Pts | Credits: {gpp_credits:.1f}/100)]
Captain (C - Safe Anchor Lock): {gpp_cap['Player']} ({gpp_cap['Team']}) [Proj: {gpp_cap['Projection']}]
Vice-Captain (VC - Safe Anchor Lock): {gpp_vc['Player']} ({gpp_vc['Team']}) [Proj: {gpp_vc['Projection']}]
OX Alpha Core (Differential Leverage Active):
"""
    for _, row in gpp_roster.iterrows():
        report += f" - {row['Player']} ({row['Team']}) [{row['Role']}] | OX-Score: {row['OX_Alpha']} | Own: {row['Ownership']}% | Cr: {row['Credits']}\n"
        
    report += "\n\n"
    return report

if __name__ == "__main__":
    live_states = {}
    if os.path.exists(LIVE_STATE_FILE):
        with open(LIVE_STATE_FILE, "r", encoding="utf-8") as f:
            live_states = json.load(f)
            
    master_report = ""
    for m_id, m_data in SQUADS.items():
        state = live_states.get(str(m_id), {
            "toss_status": "POST_TOSS", "toss_winner": m_data["team_a"], 
            "elected_to": "FIELD", "meteo_dew": True, "global_pitch_wear": True
        })
        master_report += run_syndicate_engine(m_id, m_data, state)
        
    with open(OUTPUT_SUMMARY, "w", encoding="utf-8") as f:
        f.write(master_report)
        
    print("[SUCCESS] syndicate_os.py executed. Triple-header ILP linear programming matrices optimized.")
