import sys
io = sys.stdin
if not hasattr(io, 'buffer'):
    import io as _io
    sys.stdin.buffer = _io.BytesIO()
if not hasattr(sys.stdout, 'buffer'):
    import io as _io
    sys.stdout.buffer = _io.BytesIO()

import os
import requests
import pandas as pd
import numpy as np
import pulp as lp
from collections import Counter
from mcp.server.mcpserver import MCPServer as FastMCP

mcp = FastMCP("Cricket Syndicate Server")

WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket\Syndicate_Batch_Processor"
os.makedirs(WORKSPACE_DIR, exist_ok=True)

NAM_ZIM_POOL = [
    {"name": "Z Green", "role": "WK", "team": "NAM", "credits": 6.0, "points": 125.0}, {"name": "T Marumani", "role": "WK", "team": "ZIM", "credits": 7.5, "points": 118.0},
    {"name": "J Frylinck", "role": "BAT", "team": "NAM", "credits": 7.0, "points": 182.0}, {"name": "A Volschenk", "role": "BAT", "team": "NAM", "credits": 8.0, "points": 139.0},
    {"name": "L Steenkamp", "role": "BAT", "team": "NAM", "credits": 7.5, "points": 89.0}, {"name": "B Curran", "role": "BAT", "team": "ZIM", "credits": 6.0, "points": 164.0},
    {"name": "I Kaia", "role": "BAT", "team": "ZIM", "credits": 7.5, "points": 52.0}, {"name": "B Bennett", "role": "AR", "team": "ZIM", "credits": 7.5, "points": 238.0},
    {"name": "G Erasmus", "role": "AR", "team": "NAM", "credits": 8.0, "points": 204.0}, {"name": "J Smit", "role": "AR", "team": "NAM", "credits": 8.0, "points": 155.0},
    {"name": "J Nicol Loftie-Eaton", "role": "AR", "team": "NAM", "credits": 7.5, "points": 48.0}, {"name": "J Balt", "role": "AR", "team": "NAM", "credits": 6.5, "points": 8.0},
    {"name": "B Evans", "role": "AR", "team": "ZIM", "credits": 7.5, "points": 315.0}, {"name": "W Madhevere", "role": "AR", "team": "ZIM", "credits": 7.5, "points": 166.0},
    {"name": "S Raza", "role": "AR", "team": "ZIM", "credits": 9.0, "points": 165.0}, {"name": "R Burl", "role": "AR", "team": "ZIM", "credits": 7.5, "points": 146.0},
    {"name": "K Matigimu", "role": "AR", "team": "ZIM", "credits": 7.5, "points": 18.0}, {"name": "R Trumpelmann", "role": "BOWL", "team": "NAM", "credits": 6.0, "points": 174.0},
    {"name": "J Brassell", "role": "BOWL", "team": "NAM", "credits": 7.0, "points": 68.0}, {"name": "M Heingo", "role": "BOWL", "team": "NAM", "credits": 6.5, "points": 97.0},
    {"name": "B Muzarabani", "role": "BOWL", "team": "ZIM", "credits": 8.0, "points": 82.0}, {"name": "W Masakadza", "role": "BOWL", "team": "ZIM", "credits": 7.5, "points": 58.0}
]

ENG_IRE_POOL = [
    {"name": "A Hunter", "role": "WK", "team": "IRE-W", "credits": 7.5, "points": 94.0}, {"name": "G Lewis", "role": "BAT", "team": "IRE-W", "credits": 8.5, "points": 113.0},
    {"name": "R Stokell", "role": "BAT", "team": "IRE-W", "credits": 7.5, "points": 96.0}, {"name": "L Paul", "role": "BAT", "team": "IRE-W", "credits": 8.0, "points": 45.0},
    {"name": "A Tector", "role": "BAT", "team": "IRE-W", "credits": 8.0, "points": 31.0}, {"name": "M Bouchier", "role": "BAT", "team": "ENG-W", "credits": 6.0, "points": 178.0},
    {"name": "S Dunkley", "role": "BAT", "team": "ENG-W", "credits": 8.0, "points": 139.0}, {"name": "A Capsey", "role": "BAT", "team": "ENG-W", "credits": 8.0, "points": 81.0},
    {"name": "O Prendergast", "role": "AR", "team": "IRE-W", "credits": 9.0, "points": 75.0}, {"name": "G Dempsey", "role": "AR", "team": "IRE-W", "credits": 7.5, "points": 0.0},
    {"name": "C Dean", "role": "AR", "team": "ENG-W", "credits": 7.0, "points": 113.0}, {"name": "F Kemp", "role": "AR", "team": "ENG-W", "credits": 7.5, "points": 78.0},
    {"name": "M Villiers", "role": "AR", "team": "ENG-W", "credits": 6.0, "points": 55.0}, {"name": "D Gibson", "role": "AR", "team": "ENG-W", "credits": 6.5, "points": 19.0},
    {"name": "J Grewcock", "role": "AR", "team": "ENG-W", "credits": 6.5, "points": 17.0}, {"name": "C Murray", "role": "BOWL", "team": "IRE-W", "credits": 8.0, "points": 130.0},
    {"name": "L Little", "role": "BOWL", "team": "IRE-W", "credits": 8.0, "points": 17.0}, {"name": "J Maguire", "role": "BOWL", "team": "IRE-W", "credits": 8.0, "points": 14.0},
    {"name": "K McCartney", "role": "BOWL", "team": "IRE-W", "credits": 8.0, "points": 14.0}, {"name": "T Corteen-Coleman", "role": "BOWL", "team": "ENG-W", "credits": 8.0, "points": 20.0},
    {"name": "I Wong", "role": "BOWL", "team": "ENG-W", "credits": 6.5, "points": 104.0}, {"name": "R Macdonald-Gay", "role": "BOWL", "team": "ENG-W", "credits": 7.0, "points": 0.0}
]

IND_HK_POOL = [
    {"name": "R Ghosh", "role": "WK", "team": "IND-W", "credits": 8.0, "points": 18.0},
    {"name": "Y Daswani", "role": "WK", "team": "HK-W", "credits": 7.0, "points": 58.0},
    {"name": "S Shahzad", "role": "WK", "team": "HK-W", "credits": 6.5, "points": 24.0},
    {"name": "S Verma", "role": "BAT", "team": "IND-W", "credits": 9.0, "points": 140.0},
    {"name": "S Mandhana", "role": "BAT", "team": "IND-W", "credits": 8.5, "points": 65.0},
    {"name": "P Rawal", "role": "BAT", "team": "IND-W", "credits": 7.5, "points": 48.0},
    {"name": "B Fulmali", "role": "BAT", "team": "IND-W", "credits": 8.0, "points": 25.0},
    {"name": "H Kaur", "role": "BAT", "team": "IND-W", "credits": 9.0, "points": 9.0},
    {"name": "N Miles", "role": "BAT", "team": "HK-W", "credits": 7.0, "points": 0.0},
    {"name": "M Hill", "role": "BAT", "team": "HK-W", "credits": 7.5, "points": 2.0},
    {"name": "Kamalini", "role": "WK", "team": "IND-W", "credits": 7.0, "points": 0.0},
    {"name": "M Lamplough", "role": "AR", "team": "HK-W", "credits": 6.5, "points": 233.0},
    {"name": "K Chan", "role": "AR", "team": "HK-W", "credits": 8.0, "points": 140.0},
    {"name": "D Sharma", "role": "AR", "team": "IND-W", "credits": 8.5, "points": 134.0},
    {"name": "M Bibi", "role": "AR", "team": "HK-W", "credits": 6.0, "points": 25.0},
    {"name": "N Sharma", "role": "BOWL", "team": "IND-W", "credits": 6.5, "points": 126.0},
    {"name": "S Charani", "role": "BOWL", "team": "IND-W", "credits": 8.0, "points": 95.0},
    {"name": "P Rawat", "role": "BOWL", "team": "IND-W", "credits": 6.5, "points": 47.0},
    {"name": "A Siu", "role": "BOWL", "team": "HK-W", "credits": 9.0, "points": 106.0},
    {"name": "J Kaur", "role": "BOWL", "team": "HK-W", "credits": 6.5, "points": 20.0},
    {"name": "R Venkatesh", "role": "BOWL", "team": "HK-W", "credits": 6.0, "points": 13.0},
    {"name": "I Sahar", "role": "BOWL", "team": "HK-W", "credits": 6.0, "points": 0.0}
]

@mcp.tool()
def fetch_venue_weather(city_name: str) -> str:
    """Fetches real-time atmospheric conditions for venue adjustment models."""
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1", timeout=5).json()
        if not geo.get("results"): return f"City {city_name} not found."
        res = geo["results"][0]
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={res['latitude']}&longitude={res['longitude']}&current_weather=true", timeout=5).json()
        cw = w.get("current_weather", {})
        return f"Venue: {city_name} | Temp: {cw.get('temperature')}°C | Wind Speed: {cw.get('windspeed')} km/h"
    except Exception as e:
        return f"Weather fetch failed: {e}"

@mcp.tool()
def run_syndicate_optimization(match_name: str) -> str:
    """Solves the strict 398% pOWN ILP matrix for a selected match slate (NAM vs ZIM, ENG-W vs IRE-W, IND-W vs HK-W)."""
    pools = {"NAM vs ZIM": NAM_ZIM_POOL, "ENG-W vs IRE-W": ENG_IRE_POOL, "IND-W vs HK-W": IND_HK_POOL}
    if match_name not in pools:
        return f"Unknown match slate. Choose from: {list(pools.keys())}"
        
    df = pd.DataFrame(pools[match_name]).rename(columns={"points": "proj"})
    df["proj"] = df["proj"].astype(float)
    mx = df["proj"].max()
    df["base_pown"] = (df["proj"] / mx) * 85.0
    
    sims, counts, c_hist = [], {i: 0 for i in df.index}, Counter()
    num_sims = 100
    
    for _ in range(num_sims):
        prob = lp.LpProblem("Sim", lp.LpMaximize)
        p, c, vc = [{i: lp.LpVariable(f"{prefix}_{i}", cat="Binary") for i in df.index} for prefix in ("p", "c", "vc")]
        
        noisy = {i: max(0.0, (r["proj"] + np.random.normal(0, 0.10 * r["proj"])) * (0.85 if c_hist[i] > num_sims * 0.25 else 1.0)) for i, r in df.iterrows()}
        prob += lp.lpSum([noisy[i]*p[i] + noisy[i]*c[i] + 0.5*noisy[i]*vc[i] for i in df.index])
        
        prob += lp.lpSum(p.values()) == 11
        prob += lp.lpSum([df.loc[i, "credits"] * p[i] for i in df.index]) <= 100.0
        prob += lp.lpSum([df.loc[i, "base_pown"] * p[i] for i in df.index]) <= 398.0
        prob += lp.lpSum(c.values()) == 1
        prob += lp.lpSum(vc.values()) == 1
        
        for i in df.index: prob += c[i] + vc[i] <= p[i]
        for role, mn, mx_role in [("WK", 1, 4), ("BAT", 1, 4), ("AR", 1, 6), ("BOWL", 2, 6)]:
            prob += lp.lpSum([p[i] for i in df[df["role"] == role].index]) >= mn
            prob += lp.lpSum([p[i] for i in df[df["role"] == role].index]) <= mx_role
            
        prob.solve(lp.PULP_CBC_CMD(msg=False))
        if lp.LpStatus[prob.status] == "Optimal":
            sel = [i for i in df.index if p[i].varValue > 0.5]
            c_pick = [i for i in df.index if c[i].varValue > 0.5][0]
            vc_pick = [i for i in df.index if vc[i].varValue > 0.5][0]
            c_hist[c_pick] += 1
            sims.append((tuple(sorted(sel)), c_pick, vc_pick))
            
    if not sims: return f"Optimization failed for {match_name}."
    best, _ = Counter(sims).most_common(1)[0]
    squad = df.loc[list(best[0])]
    capt, vcapt = df.loc[best[1], "name"], df.loc[best[2], "name"]
    
    # Save CSV export automatically
    squad_export = squad['name'].tolist() + [capt, vcapt]
    cols = [f"Player_{i+1}" for i in range(11)] + ["Captain", "Vice_Captain"]
    pd.DataFrame([squad_export], columns=cols).to_csv(os.path.join(WORKSPACE_DIR, f"MCP_398_{match_name.replace(' ', '_')}.csv"), index=False)
    
    output = f"Slate: {match_name}\nCaptain: {capt} | VC: {vcapt}\nTotal pOWN: {squad['base_pown'].sum():.1f}%\nCSV Exported to Workspace.\n\nLineup:\n"
    for _, row in squad.iterrows():
        output += f"- {row['name']} ({row['role']}, {row['team']}) [pOWN: {row['base_pown']:.1f}%]\n"
    return output

if __name__ == "__main__":
    mcp.run()
