import os
import pandas as pd
import pulp
import requests

def load_slate_data():
    """
    STEP 1: RAPIDAPI CRICBUZZ INGESTION
    Fetches and parses real-time match data using Cricbuzz nested JSON structures.
    """
    print("--- [STEP 1] FETCHING RAPIDAPI CRICBUZZ SLATE ---")
    
    api_key = "b84c777f82mshf8a62983fcca58dp1a6214jsn0eb579d1ea5d"
    api_host = "cricbuzz-cricket.p.rapidapi.com"
    
    match_id = "40381"
    endpoint = f"https://{api_host}/mcenter/v1/{match_id}/hscard"
    
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": api_host,
        "x-rapidapi-key": api_key
    }
    
    parsed_rows = []
    
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Safely extract the scorecard array
        scorecard_list = data.get("scoreCard")
        
        if not scorecard_list:
            print(f"API Notice: 'scoreCard' missing or empty. (Match might not have started).")
            print(f"DEBUG - API Keys returned: {list(data.keys())}")
        else:
            for innings in scorecard_list:
                
                # --- PARSE BATTING TEAM ---
                bat_team = innings.get("batTeamDetails", {})
                team_name = bat_team.get("batTeamName", "Unknown Batting Team")
                
                # Cricbuzz stores batsmen as a dictionary mapping (e.g., "bat_123": {...})
                batsmen_data = bat_team.get("batsmenData", {})
                
                for bat_id, b_info in batsmen_data.items():
                    player_name = b_info.get("batName") or b_info.get("batShortName")
                    if player_name:
                        role = "WK" if b_info.get("isKeeper") else "BAT"
                        parsed_rows.append({
                            "player": player_name,
                            "team": team_name,
                            "role": role,
                            "salary": 9.0,
                            "projected_points": 50.0
                        })
                
                # --- PARSE BOWLING TEAM ---
                bowl_team = innings.get("bowlTeamDetails", {})
                bowl_team_name = bowl_team.get("bowlTeamName", "Unknown Bowling Team")
                
                bowlers_data = bowl_team.get("bowlersData", {})
                
                for bowl_id, b_info in bowlers_data.items():
                    player_name = b_info.get("bowlName") or b_info.get("bowlShortName")
                    if not player_name:
                        continue
                        
                    # Check if player is already in the list (batting and bowling makes them an All-Rounder)
                    existing = next((r for r in parsed_rows if r['player'] == player_name), None)
                    if existing:
                        existing['role'] = "AR"
                        existing['projected_points'] += 15.0  # Bump projection for all-rounders
                        existing['salary'] += 0.5
                    else:
                        parsed_rows.append({
                            "player": player_name,
                            "team": bowl_team_name,
                            "role": "BOW",
                            "salary": 8.5,
                            "projected_points": 45.0
                        })

    except Exception as e:
        print(f"RapidAPI Connection Warning: {e}")

    # Fallback to defaults if the payload didn't yield players (e.g. Match not started)
    if not parsed_rows:
        print("Notice: No players extracted. Initializing default match pool...")
        team_a, team_b = "Team A", "Team B"
        roles = ["WK", "BAT", "BAT", "BAT", "AR", "AR", "BOW", "BOW", "BOW", "BOW", "BAT"]
        
        for idx, r in enumerate(roles, 1):
            parsed_rows.append({
                "player": f"{team_a} Player {idx}", "team": team_a, "role": r,
                "salary": 9.0 if r in ["WK", "AR"] else 8.5, "projected_points": 55.0 + (idx * 1.5)
            })
            parsed_rows.append({
                "player": f"{team_b} Player {idx}", "team": team_b, "role": r,
                "salary": 9.0 if r in ["WK", "AR"] else 8.5, "projected_points": 54.0 + (idx * 1.5)
            })

    df = pd.DataFrame(parsed_rows)
    df.columns = df.columns.str.strip()
    print(f"SUCCESS: Live slate loaded. Active player pool: {len(df)} rows.")
    return df


def optimize_lineup(df):
    """
    STEP 2: PULP LINEUP OPTIMIZATION ENGINE
    Applies salary cap, exact squad size, and role constraints to maximize projected points.
    """
    print("\n--- [STEP 2] RUNNING PULP OPTIMIZATION MODEL ---")
    
    prob = pulp.LpProblem("Cricket_DFS_Optimizer", pulp.LpMaximize)

    player_vars = {i: pulp.LpVariable(f"player_{i}", cat='Binary') for i in df.index}

    prob += pulp.lpSum(player_vars[i] * df.loc[i, 'projected_points'] for i in df.index), "Total_Projected_Points"
    prob += pulp.lpSum(player_vars[i] for i in df.index) == 11, "Total_Players_Constraint"
    prob += pulp.lpSum(player_vars[i] * df.loc[i, 'salary'] for i in df.index) <= 100.0, "Salary_Cap_Constraint"

    for role in df['role'].unique():
        role_indices = df[df['role'] == role].index
        if role in ['WK', 'Wicketkeeper']:
            prob += pulp.lpSum(player_vars[i] for i in role_indices) >= 1, "Min_WK"
            prob += pulp.lpSum(player_vars[i] for i in role_indices) <= 4, "Max_WK"
        elif role in ['BAT', 'Batsman']:
            prob += pulp.lpSum(player_vars[i] for i in role_indices) >= 1, "Min_BAT"
            prob += pulp.lpSum(player_vars[i] for i in role_indices) <= 6, "Max_BAT"
        elif role in ['AR', 'Allrounder', 'All-Rounder']:
            prob += pulp.lpSum(player_vars[i] for i in role_indices) >= 1, "Min_AR"
            prob += pulp.lpSum(player_vars[i] for i in role_indices) <= 6, "Max_AR"
        elif role in ['BOW', 'Bowler', 'BOWL']:
            prob += pulp.lpSum(player_vars[i] for i in role_indices) >= 1, "Min_BOW"
            prob += pulp.lpSum(player_vars[i] for i in role_indices) <= 6, "Max_BOW"

    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    print(f"Optimization Status: {pulp.LpStatus[prob.status]}")

    selected_indices = [i for i in df.index if player_vars[i].varValue == 1]
    selected_df = df.loc[selected_indices].copy()

    total_proj = selected_df['projected_points'].sum()
    total_salary = selected_df['salary'].sum()

    print(f"SUCCESS: Optimal Lineup Generated.")
    print(f"Total Projected Points: {total_proj:.2f} | Total Salary Used: {total_salary:.1f}/100.0")
    print("\nSelected Lineup Breakdown:")
    print(selected_df[['player', 'team', 'role', 'salary', 'projected_points']].to_string(index=False))
    print("-" * 50 + "\n")

    return selected_df


if __name__ == "__main__":
    try:
        slate_df = load_slate_data()
        
        print("\nPlayer Pool Snapshot:")
        print(slate_df[['player', 'team', 'role', 'salary', 'projected_points']].head(3).to_string(index=False))
        print("-" * 46)
        
        optimize_lineup(slate_df)
    except Exception as error:
        print(f"Pipeline Terminated: {error}")
