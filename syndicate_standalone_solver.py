import os, json, requests, pandas as pd
import pulp as lp
from collections import defaultdict

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
MATCH_ID = "102040"
API_KEY  = "b84c777f82mshf8a62983fcca58dp1a6214jsn0eb579d1ea5d"   
RAPID_HOST = "free-cricbuzz-cricket-api.p.rapidapi.com"

# ----------------------------------------------------------------------
# 1. FETCH DATA FROM THE API
# ----------------------------------------------------------------------
def fetch_match_info(matchid):
    url = f"https://{RAPID_HOST}/cricket-match-info"
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPID_HOST,
        "x-rapidapi-key": API_KEY,
    }
    params = {"matchid": matchid}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()                 
    return resp.json()

# ----------------------------------------------------------------------
# 2. PARSE PLAYERS FROM THE RESPONSE
# ----------------------------------------------------------------------
def parse_players(data):
    players = []

    if "teams" in data and isinstance(data["teams"], list):
        for t in data["teams"]:
            tname = t.get("teamName") or t.get("name") or "Unknown"
            for p in t.get("players", []):
                players.append({ **p, "team": tname })
    elif "team1Players" in data or "team2Players" in data:
        for key, tname in [("team1Players","Team 1"), ("team2Players","Team 2")]:
            for p in data.get(key, []):
                players.append({ **p, "team": tname })
    else:
        def search(obj):
            found = []
            if isinstance(obj, dict):
                for v in obj.values():
                    found.extend(search(v))
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict) and 'name' in item:
                        found.append(item)
                    else:
                        found.extend(search(item))
            return found
        raw_players = search(data)
        for p in raw_players:
            players.append({ **p, "team": p.get("team", "Unknown") })

    if not players:
        print("⚠️  Could not find player data. Raw example:")
        print(data)
        raise SystemExit("Cannot continue without player list – adjust parser.")

    def map_role(raw, is_keeper):
        if is_keeper:
            return "WK"
        r = str(raw or "").lower()
        if "keeper" in r or "wk" in r:
            return "WK"
        if "all" in r:
            return "AR"
        if "bowl" in r:
            return "BOWL"
        return "BAT"

    df_rows = []
    for p in players:
        is_keeper = p.get("isKeeper", False) or p.get("playerRole") in ["Wicketkeeper"]
        df_rows.append({
            "name": p.get("name") or p.get("playerName") or f"Player_{len(df_rows)}",
            "role": map_role(p.get("role", ""), is_keeper),
            "team": p.get("team", "Unknown"),
        })

    return pd.DataFrame(df_rows)

# ----------------------------------------------------------------------
# 3. ASSIGN COSTS & PROJECTIONS
# ----------------------------------------------------------------------
def assign_costs_and_projections(df):
    base_cost = {"WK": 10.0, "BAT": 11.0, "AR": 9.5, "BOWL": 8.5}

    rows = []
    for idx, row in df.iterrows():
        role = row["role"]
        seed = sum(ord(c) for c in row["name"]) % 7
        cost = base_cost[role] + (seed * 0.2)   

        batting_team = (row["team"] in ["IND", "AUS", "ENG"])  
        proj_points = round(
            (30 if role in ["BAT", "WK"] else 25 if role == "AR" else 20)
            + seed * 1.3 + (3 if batting_team else 0),
            1
        )
        rows.append([row["name"], row["role"], row["team"], round(cost,1), proj_points])
    return pd.DataFrame(rows, columns=["name","role","team","cost","proj_points"])

# ----------------------------------------------------------------------
# 4. OPTIMIZER (PATCHED)
# ----------------------------------------------------------------------
def optimize_team(df):
    df["id"] = range(len(df))
    ids = df["id"].tolist()
    role_map = dict(zip(df["id"], df["role"]))
    team_map = dict(zip(df["id"], df["team"]))
    cost_map = dict(zip(df["id"], df["cost"]))
    pts_map  = dict(zip(df["id"], df["proj_points"]))

    prob = lp.LpProblem("DreamTeam_Optimizer", lp.LpMaximize)

    x = lp.LpVariable.dicts("pick", ids, 0, 1, cat="Integer")
    cap = lp.LpVariable.dicts("captain", ids, 0, 1, cat="Integer")
    vc = lp.LpVariable.dicts("vice", ids, 0, 1, cat="Integer")

    # Fixed Variable References
    prob.setObjective(
        lp.lpSum(x[i]  * pts_map[i] for i in ids) +
        lp.lpSum(cap[i]* pts_map[i] for i in ids) +
        lp.lpSum(vc[i] * pts_map[i] * 0.5 for i in ids)
    )

    prob += lp.lpSum(x[i] for i in ids) == 11                   
    prob += lp.lpSum(x[i] * cost_map[i] for i in ids) <= 100             

    role_groups = defaultdict(list)
    for i in ids:
        role_groups[role_map[i]].append(i)
    prob += lp.lpSum(x[i] for i in role_groups['WK'])  >= 1
    prob += lp.lpSum(x[i] for i in role_groups['WK'])  <= 4
    prob += lp.lpSum(x[i] for i in role_groups['BAT']) >= 3
    prob += lp.lpSum(x[i] for i in role_groups['BAT']) <= 6
    prob += lp.lpSum(x[i] for i in role_groups['AR'])  >= 1
    prob += lp.lpSum(x[i] for i in role_groups['AR'])  <= 4
    prob += lp.lpSum(x[i] for i in role_groups['BOWL'])>= 3
    prob += lp.lpSum(x[i] for i in role_groups['BOWL'])<= 6

    for team_set in set(team_map.values()):
        prob += lp.lpSum(x[i] for i in ids if team_map[i] == team_set) <= 7

    prob += lp.lpSum(cap[i] for i in ids) == 1
    prob += lp.lpSum(vc[i] for i in ids) == 1
    for i in ids:
        prob += cap[i] <= x[i]          
        prob += vc[i]  <= x[i]          
        prob += cap[i] + vc[i] <= 1     

    prob.solve(lp.PULP_CBC_CMD(msg=False))
    if lp.LpStatus[prob.status] != "Optimal":
        raise ValueError(f"Solver failed: {lp.LpStatus[prob.status]}")

    selected = [i for i in ids if prob.variablesDict()[f"pick_{i}"].value() == 1]
    captain_id = next(i for i in ids if prob.variablesDict()[f"captain_{i}"].value() == 1)
    vice_id    = next(i for i in ids if prob.variablesDict()[f"vice_{i}"].value() == 1)

    out = df[df['id'].isin(selected)].copy()
    out['is_captain'] = out['id'] == captain_id
    out['is_vice']    = out['id'] == vice_id
    return out.sort_values(['role', 'proj_points'], ascending=[True, False])

# ----------------------------------------------------------------------
# 5. MAIN EXECUTION (PATCHED)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print(f"🔍 Fetching match {MATCH_ID}...")
    try:
        data = fetch_match_info(MATCH_ID)
    except Exception as e:
        print("❌ API call failed:", e)
        raise

    df_players = parse_players(data)
    print(f"✅ Found {len(df_players)} players")

    df_team = assign_costs_and_projections(df_players)
    best_team = optimize_team(df_team)

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🏆 WINNING DREAM TEAM")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for _, p in best_team.iterrows():
        tag = ""
        if p['is_captain']:
            tag = "   (C) ★"
        elif p['is_vice']:
            tag = "   (VC)"
        print(f"{p['role']:4} | {p['name']:25} | {p['team']:5} | cost {p['cost']:.1f} | proj {p['proj_points']:5.1f}{tag}")

    total_cost = best_team['cost'].sum()
    
    # Fixed Captain Math
    total_proj = best_team['proj_points'].sum() + best_team.loc[best_team['is_captain'],'proj_points'].values[0] * 1.0 + best_team.loc[best_team['is_vice'],'proj_points'].values[0] * 0.5
    print(f"\nTotal Cost:  {total_cost:.1f} / 100")
    print(f"Expected Points (incl C/VC): {total_proj:.1f}")

    best_team.to_csv("dream_team.csv", index=False)
    print("💾 Saved to dream_team.csv")
