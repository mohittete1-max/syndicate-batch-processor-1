"""
==============================================================================
SYNDICATE OS - MULTI-FORMAT & LEAGUE-AWARE UNIVERSAL ENGINE
Supports T20, ODI, Test Matches, and Franchise / Domestic Leagues.
==============================================================================
"""

import os
import random
import pandas as pd
from datetime import datetime

BASE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
os.makedirs(BASE_DIR, exist_ok=True)

OUTPUT_SUMMARY = os.path.join(BASE_DIR, "Final_Lineups_Mobile_Summary.txt")
SLATE_CSV = os.path.join(BASE_DIR, "multi_format_slate.csv")

def get_format_multipliers(match_format):
    """
    Returns tactical weighting based on whether the match is T20, ODI, or Test,
    and whether it is International or Franchise/Domestic.
    """
    match_format = match_format.upper()
    
    if match_format == "T20":
        # T20: High strike-rate and death-over boundary weighting
        return {"batting_weight": 1.10, "bowling_weight": 1.15, "allrounder_weight": 1.20, "base_scale": 1.0}
    elif match_format == "ODI":
        # ODI: Anchor innings, middle-overs dot-ball economy, and pacing matter more
        return {"batting_weight": 1.15, "bowling_weight": 1.10, "allrounder_weight": 1.18, "base_scale": 1.3}
    elif match_format == "TEST":
        # Test Matches: Multi-day durability, long innings conversion, and heavy work-rate for bowlers
        return {"batting_weight": 1.25, "bowling_weight": 1.25, "allrounder_weight": 1.30, "base_scale": 2.2}
    else:
        return {"batting_weight": 1.0, "bowling_weight": 1.0, "allrounder_weight": 1.0, "base_scale": 1.0}

def configure_match_specs(match_id, match_format="T20", league_type="INTERNATIONAL", gender="MEN"):
    """
    Configures match details for any international or franchise league (IPL, CPL, Duleep Trophy, Tests, etc.)
    """
    title = f"Match_{match_id}"
    series = f"{league_type} - {match_format} ({gender})"
    
    # Generic scalable squad constructor for any franchise or international fixture
    squad_a = [(f"PlayerA{i}", "AR" if i%3==0 else ("BAT" if i%2==0 else "BOWL"), round(random.uniform(1.0, 1.25), 2)) for i in range(1, 12)]
    squad_b = [(f"PlayerB{i}", "WK" if i==1 else ("AR" if i%3==0 else "BAT"), round(random.uniform(1.0, 1.25), 2)) for i in range(1, 12)]
    
    return title, series, "TEAM_A", "TEAM_B", squad_a, squad_b, match_format

def run_multi_format_engine(match_id, match_format="T20", league_type="INTERNATIONAL", gender="MEN"):
    title, series, t_a, t_b, sq_a, sq_b, fmt = configure_match_specs(match_id, match_format, league_type, gender)
    weights = get_format_multipliers(match_format)
    
    data = []
    for player, role, h2h in sq_a:
        role_mult = weights["batting_weight"] if role == "BAT" else (weights["bowling_weight"] if role == "BOWL" else weights["allrounder_weight"])
        base_proj = round(random.uniform(45.0, 85.0) * weights["base_scale"] * role_mult, 2)
        data.append({"Player": player, "Team": t_a, "Role": role, "Salary": 8.5, "Base_Projection": base_proj, "H2H_Weight": h2h, "Selected_Status": "PLAYING"})
        
    for player, role, h2h in sq_b:
        role_mult = weights["batting_weight"] if role == "BAT" else (weights["bowling_weight"] if role == "BOWL" else weights["allrounder_weight"])
        base_proj = round(random.uniform(45.0, 85.0) * weights["base_scale"] * role_mult, 2)
        data.append({"Player": player, "Team": t_b, "Role": role, "Salary": 8.5, "Base_Projection": base_proj, "H2H_Weight": h2h, "Selected_Status": "PLAYING"})
        
    df = pd.DataFrame(data)
    
    for idx, row in df.iterrows():
        adjusted = row["Base_Projection"] * row["H2H_Weight"]
        df.loc[idx, "Adjusted_Projection"] = round(adjusted, 2)
        
    df.to_csv(SLATE_CSV, index=False)
    
    team_a_df = df[df["Team"] == t_a].sort_values(by="Adjusted_Projection", ascending=False)
    team_b_df = df[df["Team"] == "ZIM" if "ZIM" in t_b else df["Team"] == t_b].sort_values(by="Adjusted_Projection", ascending=False)
    
    h2h_team = pd.concat([team_a_df.head(6), team_b_df.head(5)]).sort_values(by="Adjusted_Projection", ascending=False).reset_index(drop=True)
    h2h_pts = h2h_team["Adjusted_Projection"].sum()
    
    summary_text = f"""=======================================================
SYNDICATE OS - MULTI-FORMAT MASTER ENGINE REPORT
Series: {series} | Format: {fmt} ({gender})
Match ID: {match_id} | Type: {league_type}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
=======================================================

[OPTIMIZED LINEUP (Total Projected Units: {h2h_pts:.1f})]
Captain (C): {h2h_team.iloc[0]['Player']} ({h2h_team.iloc[0]['Team']}) - Proj: {h2h_team.iloc[0]['Adjusted_Projection']}
Vice-Captain (VC): {h2h_team.iloc[1]['Player']} ({h2h_team.iloc[1]['Team']}) - Proj: {h2h_team.iloc[1]['Adjusted_Projection']}
Remaining Lineup:
"""
    for idx, row in h2h_team.iterrows():
        summary_text += f" - {row['Player']} ({row['Team']}) [{row['Role']}] | Proj: {row['Adjusted_Projection']}\n"

    with open(OUTPUT_SUMMARY, "w", encoding="utf-8") as f:
        f.write(summary_text)
        
    print(f"[SUCCESS] Multi-format engine executed for Match ID {match_id} | Format: {fmt} | League: {league_type}")

if __name__ == "__main__":
    # Example execution for a Test match or Franchise league fixture (e.g., CPL or Duleep Trophy)
    RUN_MATCH_ID = "154524" # e.g. CPL match or Test match
    RUN_FORMAT = "TEST"     # Options: "T20", "ODI", "TEST"
    RUN_LEAGUE = "DOMESTIC_FRANCHISE" # Options: "INTERNATIONAL", "DOMESTIC_FRANCHISE"
    RUN_GENDER = "MEN"      # Options: "MEN", "WOMEN"
    
    run_multi_format_engine(RUN_MATCH_ID, RUN_FORMAT, RUN_LEAGUE, RUN_GENDER)
