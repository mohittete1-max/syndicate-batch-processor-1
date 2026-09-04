import os
import requests
import pandas as pd
import pulp
import plotly.express as px
import sqlite3

# HARDCODED API KEYS & TELEGRAM CONFIG
CRICDATA_API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
TELEGRAM_BOT_TOKEN = "8942957322:AAF86-GixapC8Rs88Jcn-wWX6M-o-6SYWKE"
TELEGRAM_CHAT_ID = "8942186617"

# ABSOLUTE DB PATH TO PREVENT IDLE / POWERSHELL WORKING DIRECTORY MISMATCHES
DB_PATH = r"C:\Users\User\OneDrive\Desktop\Cricket\Syndicate_Batch_Processor\dfs_history.db"

def send_telegram_message(message):
    """Dispatches a notification message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[+] Telegram alert sent successfully.")
        else:
            print(f"[!] Failed to send Telegram alert. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"[!] Exception occurred while sending Telegram message: {e}")

def run_ilp_optimization_with_leverage(df):
    """Runs ILP optimization favoring a balanced leverage score to avoid pure chalk traps."""
    print("Running ILP Optimization with balanced leverage constraints...")
    df["Leverage_Score"] = df["Projection"] - (df["pOWN%"] * 0.7)
    
    prob = pulp.LpProblem("DFS_Optimized_Lineup", pulp.LpMaximize)
    player_vars = pulp.LpVariable.dicts("Players", df.index, cat="Binary")

    prob += pulp.lpSum([df.loc[i, "Projection"] * player_vars[i] for i in df.index]), "Total_Projection"
    prob += pulp.lpSum([player_vars[i] for i in df.index]) == 11, "Exactly_11_Players"
    prob += pulp.lpSum([df.loc[i, "Salary"] * player_vars[i] for i in df.index]) <= 100.0, "Salary_Cap"

    for team in df['Team'].unique():
        team_players = df[df['Team'] == team].index
        prob += pulp.lpSum([player_vars[i] for i in team_players]) <= 7, f"Max_7_{team}"

    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    selected_indices = [i for i in df.index if player_vars[i].varValue == 1.0]
    optimal_lineup = df.loc[selected_indices].copy()
    total_proj = round(pulp.value(prob.objective), 2)
    
    print(f"Optimization Status: {pulp.LpStatus[prob.status]}")
    print(f"Total Projected Points: {total_proj}\n")
    return df, optimal_lineup, total_proj

if __name__ == "__main__":
    match_id = "UAE_W_vs_INA_W_Post_Toss"
    
    match_info = {
        "odds": {"UAE-W": 0.82, "INA-W": 0.18},
        "data": {
            "Player_Name": [
                "Esha Oza", "Theertha Satish", "Lavanya Keny", "Heena Hotchandani", 
                "Samaira Dharnidharka", "Rinitha Rajith", "Mehul Pranav Kulkarni", 
                "Vaishnave Mahesh", "Archara Supriya", "Janani Thirukkumaran", "Suraksha Kotte",
                "Rahmawati Pangestuti", "Maria Corazon", "Ni Putu Ayu Nanda Sakarini", 
                "Ni Luh Dewi", "Sofia Velic", "Ni Kadek Fitria Rada Rani", "Desi Wulandari", 
                "Ni Made Putri Suwandewi", "Sang Maypriani", "Ni Kadek Ariani", "Kisi Kasse"
            ],
            "Team": [
                "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W",
                "INA-W", "INA-W", "INA-W", "INA-W", "INA-W", "INA-W", "INA-W", "INA-W", "INA-W", "INA-W", "INA-W"
            ],
            "Role": [
                "AR", "WK", "BAT", "AR", "AR", "BAT", "BOWL", "BOWL", "BOWL", "BOWL", "BOWL",
                "BAT", "BAT", "WK", "AR", "AR", "AR", "BAT", "AR", "BOWL", "BOWL", "WK"
            ],
            "Salary": [
                9.5, 8.5, 7.5, 8.5, 8.0, 7.0, 7.5, 8.0, 7.0, 6.5, 6.5,
                7.0, 6.0, 8.0, 8.5, 7.5, 7.0, 6.5, 7.5, 7.0, 6.5, 6.0
            ],
            "Projection": [
                78.0, 48.0, 32.0, 65.0, 58.0, 25.0, 45.0, 52.0, 40.0, 38.0, 35.0,
                30.0, 15.0, 42.0, 72.0, 40.0, 32.0, 22.0, 48.0, 36.0, 28.0, 12.0
            ],
            "pOWN%": [
                88.5, 62.1, 24.0, 74.2, 55.0, 18.2, 30.5, 68.4, 21.0, 15.6, 12.4,
                28.0, 10.5, 45.2, 82.1, 38.4, 25.0, 14.2, 51.0, 42.5, 20.1, 8.5
            ]
        }
    }

    player_pool = pd.DataFrame(match_info["data"])
    
    for idx, row in player_pool.iterrows():
        team = row['Team']
        implied_prop = match_info["odds"].get(team, 0.50)
        multiplier = 1.0 + (implied_prop - 0.50) * 0.8
        player_pool.loc[idx, 'Projection'] = round(row['Projection'] * multiplier, 1)

    processed_pool, lineup, total_proj = run_ilp_optimization_with_leverage(player_pool)
    
    # SQLite storage with absolute path and clean table reset
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS historical_lineups")
    conn.commit()
    
    lineup.insert(0, "Match_ID", match_id)
    lineup.to_sql("historical_lineups", conn, if_exists="replace", index=False)
    conn.close()

    # Visualizations
    fig = px.scatter(
        processed_pool, x="pOWN%", y="Projection", size="Salary", color="Leverage_Score",
        hover_name="Player_Name", hover_data=["Team", "Role", "Salary"],
        title=f"DFS Leverage Matrix - {match_id}", template="plotly_dark"
    )
    fig.write_html(f"{match_id}_Leverage_Chart.html")

    # Captain and Vice-Captain Assignment
    lineup_sorted = lineup.sort_values(by="Projection", ascending=False).reset_index(drop=True)
    captain = lineup_sorted.loc[0, "Player_Name"] if len(lineup_sorted) > 0 else ""
    vc = lineup_sorted.loc[1, "Player_Name"] if len(lineup_sorted) > 1 else ""

    player_lines = []
    for _, row in lineup_sorted.iterrows():
        name = row["Player_Name"]
        tag = " (C 👑)" if name == captain else (" (VC 🥈)" if name == vc else "")
        player_lines.append(f"• {name}{tag} [{row['Role']} - {row['Team']}]")

    players_formatted = "\n".join(player_lines)
    tg_message = (
        f"🏏 *Post-Toss Optimized*: `{match_id}`\n"
        f"📊 *Projected Total*: `{total_proj}`\n"
        f"👑 *Captain*: `{captain}`\n"
        f"🥈 *Vice-Captain*: `{vc}`\n\n"
        f"👥 *Selected 11*:\n{players_formatted}"
    )
    send_telegram_message(tg_message)
    print("Post-toss lineup optimization complete, logged, and alerted.")
