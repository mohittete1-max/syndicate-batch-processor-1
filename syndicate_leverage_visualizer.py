import pandas as pd
import numpy as np
import pulp as lp
from collections import Counter
import plotly.express as px

# ==========================================
# FIXTURE POOLS
# ==========================================
ENG_IRE_POOL = [
    {"name": "A Hunter", "role": "WK", "team": "IRE-W", "credits": 7.5, "points": 94},
    {"name": "K Chathli", "role": "WK", "team": "ENG-W", "credits": 6.5, "points": 0},
    {"name": "M Bouchier", "role": "BAT", "team": "ENG-W", "credits": 6.0, "points": 178},
    {"name": "S Dunkley", "role": "BAT", "team": "ENG-W", "credits": 8.0, "points": 139},
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
    {"name": "B Evans", "role": "AR", "team": "ZIM", "credits": 7.5, "points": 315},
    {"name": "B Bennett", "role": "AR", "team": "ZIM", "credits": 7.5, "points": 238},
    {"name": "G Erasmus", "role": "AR", "team": "NAM", "credits": 8.0, "points": 204},
    {"name": "J Frylinck", "role": "AR", "team": "NAM", "credits": 7.0, "points": 182},
    {"name": "S Raza", "role": "AR", "team": "ZIM", "credits": 9.0, "points": 165},
    {"name": "R Trumpelmann", "role": "BOWL", "team": "NAM", "credits": 6.0, "points": 174},
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
    {"name": "S Verma", "role": "AR", "team": "IND-W", "credits": 9.0, "points": 140},
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
# DATA PREPARATION & SOLVER
# ==========================================
def prepare_data(pool):
    df = pd.DataFrame(pool)
    df = df.rename(columns={"points": "proj"})
    max_proj = df["proj"].max()
    df["base_pown"] = (df["proj"] / max_proj) * 85.0
    return df

def generate_leverage_distribution(players_df, sim_noise=0.10, num_sims=200):
    player_optimal_counts = {i: 0 for i in players_df.index}
    
    for sim_idx in range(num_sims):
        prob = lp.LpProblem(f"Syndicate_Sim_{sim_idx}", lp.LpMaximize)
        player_vars = {i: lp.LpVariable(f"x_{i}", cat="Binary") for i in players_df.index}
        
        noisy_proj = {}
        for i, row in players_df.iterrows():
            noise = np.random.normal(0, sim_noise * row["proj"])
            noisy_proj[i] = max(0.0, row["proj"] + noise)
            
        prob += lp.lpSum([noisy_proj[i] * player_vars[i] for i in players_df.index])
        
        prob += lp.lpSum([player_vars[i] for i in players_df.index]) == 11
        prob += lp.lpSum([players_df.loc[i, "credits"] * player_vars[i] for i in players_df.index]) <= 100.0
        prob += lp.lpSum([players_df.loc[i, "base_pown"] * player_vars[i] for i in players_df.index]) <= 625.0
        
        for role, min_count, max_count in [("WK", 1, 4), ("BAT", 1, 6), ("AR", 1, 6), ("BOWL", 1, 6)]:
            role_indices = players_df[players_df["role"] == role].index
            prob += lp.lpSum([player_vars[i] for i in role_indices]) >= min_count
            prob += lp.lpSum([player_vars[i] for i in role_indices]) <= max_count
            
        prob.solve(lp.PULP_CBC_CMD(msg=False))
        
        if lp.LpStatus[prob.status] == "Optimal":
            for i in players_df.index:
                if player_vars[i].varValue > 0.5:
                    player_optimal_counts[i] += 1

    players_df["optimal_pct"] = [(player_optimal_counts[i] / num_sims) * 100 for i in players_df.index]
    players_df["leverage"] = players_df["optimal_pct"] - players_df["base_pown"]
    
    return players_df

def plot_and_save_leverage(df, match_name):
    filename = f"leverage_matrix_{match_name.replace(' ', '_').replace('-', '_')}.html"
    
    fig = px.scatter(
        df, 
        x="base_pown", 
        y="optimal_pct", 
        color="leverage",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        hover_name="name",
        hover_data={"role": True, "credits": True, "proj": True, "leverage": ":.1f", "base_pown": ":.1f", "optimal_pct": ":.1f"},
        title=f"Syndicate OS Leverage Distribution: {match_name}",
        labels={"base_pown": "Public pOWN% (Field Expectation)", "optimal_pct": "Optimal % (Engine Reality)"},
        template="plotly_dark"
    )
    
    max_val = max(df["base_pown"].max(), df["optimal_pct"].max()) + 5
    fig.add_shape(
        type="line", line=dict(dash="dash", color="white", width=1),
        x0=0, y0=0, x1=max_val, y1=max_val
    )
    
    fig.add_annotation(x=max_val*0.1, y=max_val*0.9, text="🔥 Core Tournament Value", showarrow=False, font=dict(color="green"))
    fig.add_annotation(x=max_val*0.9, y=max_val*0.1, text="⚠️ Over-Owned Traps", showarrow=False, font=dict(color="red"))
    
    fig.update_layout(height=700, width=1000)
    fig.write_html(filename)
    print(f"📊 Saved interactive visualization: {filename}")

if __name__ == "__main__":
    matches = {
        "ENG-W vs IRE-W": ENG_IRE_POOL,
        "NAM vs ZIM": NAM_ZIM_POOL,
        "IND-W vs HK-W": IND_HK_POOL
    }
    
    for match_name, pool in matches.items():
        print(f"⚙️ Running 200 Monte Carlo sims for {match_name} leverage visualization...")
        df = prepare_data(pool)
        leverage_df = generate_leverage_distribution(df, sim_noise=0.10, num_sims=200)
        plot_and_save_leverage(leverage_df, match_name)
