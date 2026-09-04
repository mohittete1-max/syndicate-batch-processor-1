import sqlite3
import pandas as pd

conn = sqlite3.connect("dfs_history.db")

print("--- All Stored Lineups ---")
df_all = pd.read_sql("SELECT Match_ID, Player_Name, Team, Role, Salary, Projection FROM historical_lineups", conn)
print(df_all.to_string(index=False))

print("\n--- Total Projected Points per Match ---")
df_proj = pd.read_sql("SELECT Match_ID, SUM(Projection) AS Total_Projection FROM historical_lineups GROUP BY Match_ID", conn)
print(df_proj.to_string(index=False))

print("\n--- Most Frequently Selected Players ---")
df_freq = pd.read_sql("SELECT Player_Name, Team, COUNT(*) AS Selection_Count FROM historical_lineups GROUP BY Player_Name ORDER BY Selection_Count DESC LIMIT 10", conn)
print(df_freq.to_string(index=False))

conn.close()
