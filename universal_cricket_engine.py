import os
import glob
import difflib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pulp

# ==============================================================================
# 1. ENVIRONMENTAL & BETTING WEIGHTING ENGINES
# ==============================================================================

class EnvironmentalEngine:
    @staticmethod
    def calculate_pitch_multiplier(pitch_type="balanced"):
        multipliers = {
            "flat": {"BAT": 1.15, "AR": 1.05, "BOWL": 0.85, "WK": 1.10},
            "green": {"BAT": 0.80, "AR": 1.15, "BOWL": 1.25, "WK": 0.90},
            "dusty": {"BAT": 0.85, "AR": 1.20, "BOWL": 1.20, "WK": 0.95},
            "pasty": {"BAT": 0.85, "AR": 1.10, "BOWL": 1.15, "WK": 0.90},
            "balanced": {"BAT": 1.00, "AR": 1.00, "BOWL": 1.00, "WK": 1.00}
        }
        return multipliers.get(pitch_type.lower(), multipliers["balanced"])

    @staticmethod
    def calculate_meteo_adjustment(humidity=60, dew_factor=False, wind_speed=15):
        bowler_swing_boost = 1.05 if humidity > 70 and wind_speed > 18 else 1.0
        bowler_dew_penalty = 0.90 if dew_factor else 1.0
        return bowler_swing_boost * bowler_dew_penalty

class VegasCasinoEngine:
    @staticmethod
    def calculate_vegas_weight(team_name, fav_team, favorite_odds=-180, underdog_odds=+150):
        if favorite_odds < 0:
            fav_implied = abs(favorite_odds) / (abs(favorite_odds) + 100)
        else:
            fav_implied = 100 / (favorite_odds + 100)
            
        dog_implied = 100 / (underdog_odds + 100) if underdog_odds > 0 else 0.5
        total = fav_implied + dog_implied
        fav_prob = fav_implied / total
        dog_prob = dog_implied / total
        
        if team_name.lower() in fav_team.lower():
            return 1.0 + (fav_prob - 0.5) * 0.4 
        else:
            return 1.0 - (0.5 - dog_prob) * 0.3 

# ==============================================================================
# 2. LINEAR PROGRAMMING OPTIMIZERS (H2H vs GPP)
# ==============================================================================

def solve_h2h_portfolio(df):
    """H2H Mode: Strives for 1000+ points and mandates 50+ floor per player."""
    df = df[df['is_playing'] == 1].reset_index(drop=True)
    if len(df) < 11: return None

    prob = pulp.LpProblem("H2H_Cash_Optimization", pulp.LpMaximize)
    player_vars = [pulp.LpVariable(f"p_{i}", cat=pulp.LpBinary) for i in range(len(df))]
    c_vars = [pulp.LpVariable(f"c_{i}", cat=pulp.LpBinary) for i in range(len(df))]
    vc_vars = [pulp.LpVariable(f"vc_{i}", cat=pulp.LpBinary) for i in range(len(df))]
    
    obj_terms = []
    for i in range(len(df)):
        base_pts = df.loc[i, 'adjusted_pts']
        obj_terms.append(player_vars[i] * base_pts)
        obj_terms.append(c_vars[i] * (base_pts * 1.0))
        obj_terms.append(vc_vars[i] * (base_pts * 0.5))
        
    prob += pulp.lpSum(obj_terms)
    
    prob += pulp.lpSum(obj_terms) >= 1000.0, "Strive_1000_Points"
    for i in range(len(df)):
        prob += player_vars[i] * df.loc[i, 'adjusted_pts'] >= 50.0 * player_vars[i]
    
    prob += pulp.lpSum(player_vars) == 11
    prob += pulp.lpSum([player_vars[i] * df.loc[i, 'credits'] for i in range(len(df))]) <= 100.0
    prob += pulp.lpSum(c_vars) == 1
    prob += pulp.lpSum(vc_vars) == 1
    
    for i in range(len(df)):
        prob += c_vars[i] <= player_vars[i]
        prob += vc_vars[i] <= player_vars[i]
        prob += c_vars[i] + vc_vars[i] <= 1
        if df.loc[i, 'role'].upper() == 'BAT':
            prob += c_vars[i] == 0
            
    wk_indices = df[df['role'].str.upper() == 'WK'].index.tolist()
    bat_indices = df[df['role'].str.upper() == 'BAT'].index.tolist()
    ar_indices = df[df['role'].str.upper() == 'AR'].index.tolist()
    bowl_indices = df[df['role'].str.upper() == 'BOWL'].index.tolist()
    
    prob += pulp.lpSum([player_vars[i] for i in wk_indices]) >= 1
    prob += pulp.lpSum([player_vars[i] for i in wk_indices]) <= 4
    prob += pulp.lpSum([player_vars[i] for i in bat_indices]) >= 1
    prob += pulp.lpSum([player_vars[i] for i in bat_indices]) <= 3 
    prob += pulp.lpSum([player_vars[i] for i in ar_indices]) >= 2
    prob += pulp.lpSum([player_vars[i] for i in ar_indices]) <= 6
    prob += pulp.lpSum([player_vars[i] for i in bowl_indices]) >= 2
    prob += pulp.lpSum([player_vars[i] for i in bowl_indices]) <= 6

    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[prob.status] != "Optimal": return None
        
    selected_rows = []
    for i in range(len(df)):
        if pulp.value(player_vars[i]) == 1:
            row = df.loc[i].copy()
            row['Multiplier_Tag'] = 'Captain (2x)' if pulp.value(c_vars[i]) == 1 else 'Vice-Captain (1.5x)' if pulp.value(vc_vars[i]) == 1 else 'Base'
            selected_rows.append(row)
            
    return pd.DataFrame(selected_rows).sort_values(by=['Multiplier_Tag', 'adjusted_pts'], ascending=[True, False]).reset_index(drop=True)

def solve_gpp_portfolio(df, max_team_ownership=180.0):
    """GPP Mode: Forces the 3% Jarvis rule and optimizes for variance/ceiling."""
    df = df[df['is_playing'] == 1].reset_index(drop=True)
    
    if 'ownership' not in df.columns:
        df['ownership'] = (df['adjusted_pts'] / df['adjusted_pts'].max()) * 45.0 
    if 'ceiling_pts' not in df.columns:
        df['ceiling_pts'] = df['adjusted_pts'] * np.where(df['role'].str.upper() == 'BOWL', 1.4, 1.25)

    if len(df) < 11: return None

    prob = pulp.LpProblem("GPP_Optimization", pulp.LpMaximize)
    player_vars = [pulp.LpVariable(f"p_{i}", cat=pulp.LpBinary) for i in range(len(df))]
    c_vars = [pulp.LpVariable(f"c_{i}", cat=pulp.LpBinary) for i in range(len(df))]
    vc_vars = [pulp.LpVariable(f"vc_{i}", cat=pulp.LpBinary) for i in range(len(df))]
    
    obj_terms = []
    for i in range(len(df)):
        ceil = df.loc[i, 'ceiling_pts']
        obj_terms.append(player_vars[i] * ceil)
        obj_terms.append(c_vars[i] * (ceil * 1.0))
        obj_terms.append(vc_vars[i] * (ceil * 0.5))
        
    prob += pulp.lpSum(obj_terms)
    
    prob += pulp.lpSum([player_vars[i] * df.loc[i, 'ownership'] for i in range(len(df))]) <= max_team_ownership
    leverage_indices = df[df['ownership'] <= 5.0].index.tolist()
    if leverage_indices:
        prob += pulp.lpSum([player_vars[i] for i in leverage_indices]) >= 1
    
    prob += pulp.lpSum(player_vars) == 11
    prob += pulp.lpSum([player_vars[i] * df.loc[i, 'credits'] for i in range(len(df))]) <= 100.0
    prob += pulp.lpSum(c_vars) == 1
    prob += pulp.lpSum(vc_vars) == 1
    for i in range(len(df)):
        prob += c_vars[i] <= player_vars[i]
        prob += vc_vars[i] <= player_vars[i]
        prob += c_vars[i] + vc_vars[i] <= 1
            
    wk_indices = df[df['role'].str.upper() == 'WK'].index.tolist()
    bat_indices = df[df['role'].str.upper() == 'BAT'].index.tolist()
    ar_indices = df[df['role'].str.upper() == 'AR'].index.tolist()
    bowl_indices = df[df['role'].str.upper() == 'BOWL'].index.tolist()
    
    prob += pulp.lpSum([player_vars[i] for i in wk_indices]) >= 1
    prob += pulp.lpSum([player_vars[i] for i in wk_indices]) <= 4
    prob += pulp.lpSum([player_vars[i] for i in bat_indices]) >= 1
    prob += pulp.lpSum([player_vars[i] for i in bat_indices]) <= 5
    prob += pulp.lpSum([player_vars[i] for i in ar_indices]) >= 1
    prob += pulp.lpSum([player_vars[i] for i in ar_indices]) <= 6
    prob += pulp.lpSum([player_vars[i] for i in bowl_indices]) >= 1
    prob += pulp.lpSum([player_vars[i] for i in bowl_indices]) <= 6

    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[prob.status] != "Optimal": return None
        
    selected_rows = []
    for i in range(len(df)):
        if pulp.value(player_vars[i]) == 1:
            row = df.loc[i].copy()
            row['Multiplier_Tag'] = 'Captain (2x)' if pulp.value(c_vars[i]) == 1 else 'Vice-Captain (1.5x)' if pulp.value(vc_vars[i]) == 1 else 'Base'
            selected_rows.append(row)
            
    return pd.DataFrame(selected_rows).sort_values(by=['Multiplier_Tag', 'ceiling_pts'], ascending=[True, False]).reset_index(drop=True)

# ==============================================================================
# 3. INTERACTIVE PLOTLY REPORT
# ==============================================================================

def generate_interactive_report(df_selected, match_name):
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Role-Wise Credits", "Efficiency Projection"), specs=[[{"type": "domain"}, {"type": "xy"}]])
    role_credits = df_selected.groupby('role')['credits'].sum().reset_index()
    fig.add_trace(go.Pie(labels=role_credits['role'], values=role_credits['credits'], hole=0.45), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_selected['credits'], y=df_selected['adjusted_pts'], mode='markers+text', text=df_selected['player_name'], textposition='top center', marker=dict(size=14, color=df_selected['adjusted_pts'], colorscale='Viridis')), row=1, col=2)
    fig.update_layout(title_text=f"Syndicate Report: {match_name}", template="plotly_dark", height=500, showlegend=False)
    fig.write_html(f"{match_name}_Report.html")

# ==============================================================================
# 4. MASTER WORKFLOW CONTROLLER
# ==============================================================================

def apply_toss_override(csv_path):
    df = pd.read_csv(csv_path)
    df['is_playing'] = 1 
    print(f"\n--- Override for {csv_path} ---")
    benched_input = input("Enter BENCHED players (comma separated) or leave blank: ").strip()
    if not benched_input:
        df.to_csv(csv_path, index=False)
        return
    benched_list = [b.strip().lower() for b in benched_input.split(",") if b.strip()]
    csv_names = df['player_name'].str.lower().tolist()
    for b_name in benched_list:
        matches = [n for n in csv_names if b_name in n]
        if not matches:
            matches = difflib.get_close_matches(b_name, csv_names, n=1, cutoff=0.4)
        if matches:
            df.loc[df['player_name'].str.lower() == matches[0], 'is_playing'] = 0
            print(f"  [-] Benched: {matches[0].title()}")
    df.to_csv(csv_path, index=False)

def run_universal_pipeline():
    print("=================================================================")
    print("       UNIVERSAL SYNDICATE ENGINE (H2H & GPP FULL MERGE)         ")
    print("=================================================================")
    
    raw_files = [f for f in glob.glob("*.csv") if not f.endswith("_Target.csv") and f != "match_squad_data.csv" and not f.endswith("H2H_Cash.csv")]
    if not raw_files:
        print("[ERROR] No raw match CSV files found.")
        return
        
    print(f"[SYSTEM] Detected {len(raw_files)} fixtures in workspace.\n")
    
    # --- SLATE SELECTOR ---
    for idx, file in enumerate(raw_files):
        print(f"  [{idx + 1}] {file.replace('.csv', '')}")
        
    selection = input("\nEnter match numbers to run (e.g., 1, 3, 4) or type 'all': ").strip().lower()
    
    selected_files = []
    if selection == 'all':
        selected_files = raw_files
    else:
        try:
            indices = [int(i.strip()) - 1 for i in selection.split(",") if i.strip().isdigit()]
            selected_files = [raw_files[i] for i in indices if 0 <= i < len(raw_files)]
        except:
            print("[ERROR] Invalid selection. Defaulting to 'all'.")
            selected_files = raw_files
            
    if not selected_files:
        print("[ERROR] No matches selected. Exiting.")
        return
        
    print(f"\n[SYSTEM] Locked onto {len(selected_files)} fixture(s).")
    # ----------------------

    mode = input("Select Execution Mode - [1] H2H Cash | [2] GPP | [3] ALL (Both): ").strip().lower()
    override = input("Enable Manual Toss Override? (y/n): ").strip().lower()
    
    for file in selected_files:
        match_name = file.replace(".csv", "")
        print("\n" + "=" * 65)
        print(f"> PROCESSING: {match_name}")
        
        if override == 'y': apply_toss_override(file)
            
        df = pd.read_csv(file)
        if 'projected_points' not in df.columns: df['projected_points'] = 45.0
        if 'is_playing' not in df.columns: df['is_playing'] = 1
            
        pitch_mods = EnvironmentalEngine.calculate_pitch_multiplier("balanced")
        meteo_mod = EnvironmentalEngine.calculate_meteo_adjustment()
        fav_team = match_name.split("_vs_")[0] if "_vs_" in match_name else ""
        
        df['adjusted_pts'] = df['projected_points'].copy()
        for idx, row in df.iterrows():
            r_mod = pitch_mods.get(row['role'].upper(), 1.0)
            e_mod = meteo_mod if row['role'].upper() == 'BOWL' else 1.0
            v_mod = VegasCasinoEngine.calculate_vegas_weight(str(row.get('team', '')), fav_team)
            df.loc[idx, 'adjusted_pts'] = round(row['projected_points'] * r_mod * e_mod * v_mod, 2)
            
        if mode in ['1', '3', 'all']:
            h2h_lineup = solve_h2h_portfolio(df)
            if h2h_lineup is not None:
                h2h_lineup.to_csv(f"{match_name}_H2H_Target.csv", index=False)
                print(f"  [SAVED] {match_name}_H2H_Target.csv")
                
        if mode in ['2', '3', 'all']:
            gpp_lineup = solve_gpp_portfolio(df)
            if gpp_lineup is not None:
                gpp_lineup.to_csv(f"{match_name}_GPP_Target.csv", index=False)
                print(f"  [SAVED] {match_name}_GPP_Target.csv")
                
        report_data = h2h_lineup if mode in ['1', '3', 'all'] and h2h_lineup is not None else gpp_lineup
        if report_data is not None:
            generate_interactive_report(report_data, match_name)
        else:
            print(f"  [ERROR] Infeasible constraints for {match_name}. Check limits.")

    print("\n=================================================================")
    print("[EXECUTION COMPLETE] Operations finalized.")
    print("=================================================================")

if __name__ == "__main__":
    run_universal_pipeline()
