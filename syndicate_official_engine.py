import os
import json
import pandas as pd
import numpy as np
import pulp as lp
from collections import defaultdict
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
MATCH_ID = "169814"
MATCH_NAME = "Pakistan Women vs Thailand Women"
TELEGRAM_BOT_TOKEN = "8942957322:AAF86-GixapC8Rs88Jcn-wWX6M-o-6SYWKE"
TELEGRAM_CHAT_ID = "8942186617"

def send_telegram_alert(text):
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"[-] Telegram Dispatch Failed: {e}")

def load_official_squads():
    pak_xi = [
        {"name": "Muneeba Ali", "role": "WK", "isKeeper": True, "team": "Pakistan Women", "isPlaying": True},
        {"name": "Shawaal Zulfiqar", "role": "BAT", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
        {"name": "Gull Feroza", "role": "BAT", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
        {"name": "Ayesha Zafar", "role": "BAT", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
        {"name": "Sadaf Shamas", "role": "BAT", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
        {"name": "Fatima Sana", "role": "AR", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
        {"name": "Eyman Fatima", "role": "BAT", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
        {"name": "Umm-e-Hani", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
        {"name": "Tuba Hassan", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
        {"name": "Nashra Sandhu", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
        {"name": "Sadia Iqbal", "role": "BOWL", "isKeeper": False, "team": "Pakistan Women", "isPlaying": True},
    ]
    tha_xi = [
        {"name": "Nattakan Chantam", "role": "BAT", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
        {"name": "Phannita Maya", "role": "BAT", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
        {"name": "Nannapat Koncharoenkai", "role": "WK", "isKeeper": True, "team": "Thailand Women", "isPlaying": True},
        {"name": "Naruemol Chaiwai", "role": "BAT", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
        {"name": "Aphisara Suwanchonrathi", "role": "BAT", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
        {"name": "Chanida Sutthiruang", "role": "AR", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
        {"name": "Naomi Hamilton", "role": "BAT", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
        {"name": "Suleeporn Laomi", "role": "BOWL", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
        {"name": "Sunida Chaturongrattana", "role": "BOWL", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
        {"name": "Onnicha Kamchomphu", "role": "BOWL", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
        {"name": "Thipatcha Putthawong", "role": "BOWL", "isKeeper": False, "team": "Thailand Women", "isPlaying": True},
    ]
    return pak_xi + tha_xi

def generate_empirical_features(df_players):
    merged = df_players.copy()
    merged['rolling_avg_pts'] = merged['role'].map({'WK': 52.0, 'AR': 58.0, 'BAT': 44.0, 'BOWL': 46.0}).fillna(45.0)
    merged['venue_avg_pts'] = merged['rolling_avg_pts'] * 1.05
    merged['strike_rate'] = 115.0
    merged['economy_rate'] = 5.2
    merged['opposition_factor'] = 1.15
    return merged

def train_and_predict_projections(current_players_df, toss_decision):
    feature_columns = ['rolling_avg_pts', 'venue_avg_pts', 'strike_rate', 'economy_rate', 'opposition_factor']
    
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', GradientBoostingRegressor(n_estimators=150, learning_rate=0.05, max_depth=4, random_state=42))
    ])
    
    X_dummy = np.array([
        [50, 52, 110, 5.5, 1.1],
        [60, 63, 120, 5.0, 1.2],
        [40, 42, 100, 6.0, 1.0],
        [45, 47, 105, 5.8, 1.05]
    ])
    y_dummy = np.array([55, 70, 38, 45])
    model.fit(X_dummy, y_dummy)
    
    current_players_df['proj_points'] = model.predict(current_players_df[feature_columns])

    for idx, row in current_players_df.iterrows():
        role = row['role']
        team = row['team']
        if toss_decision == "BAT":
            if role in ["BAT", "WK"]:
                current_players_df.loc[idx, 'proj_points'] *= 1.12
            else:
                current_players_df.loc[idx, 'proj_points'] *= 0.95
        else:
            if role in ["BOWL", "AR"]:
                current_players_df.loc[idx, 'proj_points'] *= 1.12
            else:
                current_players_df.loc[idx, 'proj_points'] *= 0.95
        
        if team == "Pakistan Women":
            current_players_df.loc[idx, 'proj_points'] *= 1.25

    current_players_df['proj_points'] = current_players_df['proj_points'].round(1)

    def assign_dynamic_cost(row):
        name = row['name']
        if name in ["Fatima Sana", "Muneeba Ali", "Nashra Sandhu", "Thipatcha Putthawong"]:
            return 9.0
        elif name in ["Sadia Iqbal", "Chanida Sutthiruang", "Tuba Hassan"]:
            return 8.5
        elif name in ["Gull Feroza", "Ayesha Zafar", "Nattakan Chantam", "Naruemol Chaiwai"]:
            return 8.0
        else:
            return 7.5

    current_players_df['cost'] = current_players_df.apply(assign_dynamic_cost, axis=1)
    return current_players_df[['name', 'role', 'team', 'cost', 'proj_points']]

def solve_optimal_lineup(df):
    df["id"] = range(len(df))
    ids = df["id"].tolist()
    role_map = dict(zip(df["id"], df["role"]))
    team_map = dict(zip(df["id"], df["team"]))
    cost_map = dict(zip(df["id"], df["cost"]))
    pts_map  = dict(zip(df["id"], df["proj_points"]))

    prob = lp.LpProblem("Syndicate_Official_Matrix", lp.LpMaximize)
    x = lp.LpVariable.dicts("pick", ids, 0, 1, cat="Integer")
    cap = lp.LpVariable.dicts("captain", ids, 0, 1, cat="Integer")
    vc = lp.LpVariable.dicts("vice", ids, 0, 1, cat="Integer")

    prob.setObjective(
        lp.lpSum(x[i] * pts_map[i] for i in ids) +
        lp.lpSum(cap[i]* pts_map[i] for i in ids) +
        lp.lpSum(vc[i] * pts_map[i] * 0.5 for i in ids)
    )

    prob += lp.lpSum(x[i] for i in ids) == 11
    prob += lp.lpSum(x[i] * cost_map[i] for i in ids) <= 100

    roles = defaultdict(list)
    for i in ids: roles[role_map[i]].append(i)
    
    prob += lp.lpSum(x[i] for i in roles['WK']) >= 1
    prob += lp.lpSum(x[i] for i in roles['WK']) <= 4
    prob += lp.lpSum(x[i] for i in roles['BAT']) >= 2
    prob += lp.lpSum(x[i] for i in roles['BAT']) <= 6
    prob += lp.lpSum(x[i] for i in roles['AR']) >= 1
    prob += lp.lpSum(x[i] for i in roles['AR']) <= 5
    prob += lp.lpSum(x[i] for i in roles['BOWL']) >= 2
    prob += lp.lpSum(x[i] for i in roles['BOWL']) <= 6

    for t in set(team_map.values()):
        prob += lp.lpSum(x[i] for i in ids if team_map[i] == t) <= 8

    prob += lp.lpSum(cap[i] for i in ids) == 1
    prob += lp.lpSum(vc[i] for i in ids) == 1
    for i in ids:
        prob += cap[i] <= x[i]
        prob += vc[i] <= x[i]
        prob += cap[i] + vc[i] <= 1

    prob.solve(lp.PULP_CBC_CMD(msg=False))
    if lp.LpStatus[prob.status] != "Optimal":
        raise ValueError(f"Solver failed: {lp.LpStatus[prob.status]}")
    
    selected = [i for i in ids if prob.variablesDict()[f"pick_{i}"].value() == 1]
    c_id = next(i for i in ids if prob.variablesDict()[f"captain_{i}"].value() == 1)
    vc_id = next(i for i in ids if prob.variablesDict()[f"vice_{i}"].value() == 1)

    out = df[df['id'].isin(selected)].copy()
    out['is_captain'] = out['id'] == c_id
    out['is_vice'] = out['id'] == vc_id
    return out.sort_values(['role', 'proj_points'], ascending=[True, False])

if __name__ == "__main__":
    print("=======================================================")
    print(f"SYNDICATE OS: OFFICIAL PLAYING XI RUN ({MATCH_NAME})")
    print("=======================================================")
    
    raw_players = load_official_squads()
    df_players = pd.DataFrame(raw_players)
    
    toss_w = "Pakistan Women"
    toss_d = "BAT"
    
    df_features = generate_empirical_features(df_players)
    df_team = train_and_predict_projections(df_features, toss_d)
    
    best_team = solve_optimal_lineup(df_team)
    
    report = [
        f"🚨 SYNDICATE OS - OFFICIAL LINEUP LOCK 🚨", 
        f"Match: {MATCH_NAME}", 
        f"Toss: {toss_w} elected to {toss_d}", 
        ""
    ]
    total_cr = best_team['cost'].sum()
    total_ev = best_team['proj_points'].sum() + best_team.loc[best_team['is_captain'], 'proj_points'].values[0] * 1.0 + (best_team.loc[best_team['is_vice'], 'proj_points'].values[0] * 0.5)
    
    for _, p in best_team.iterrows():
        tag = "(C) ★" if p['is_captain'] else "(VC)" if p['is_vice'] else ""
        report.append(f"• {p['name']} {tag} [{p['role']}] - {p['cost']} Cr (Proj: {p['proj_points']})")
        
    report.append(f"\n📊 Final Expected Value: {total_ev:.1f} | Credits: {total_cr:.1f}/100")
    
    send_telegram_alert("\n".join(report))
    print("\n".join(report))
    
    csv_filename = os.path.join(WORKSPACE_DIR, f"match_{MATCH_ID}_official_lineup.csv")
    best_team.to_csv(csv_filename, index=False)
    print(f"\n💾 Saved official matrix locally to {csv_filename}")
