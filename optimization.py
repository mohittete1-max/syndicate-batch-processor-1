import pandas as pd
import pulp as pl

print(
    "Initializing Apex Alpha OS: SDS-W vs NDS-W Match Optimization Engine..."
)

# Player Pool Database for South Delhi Superstarz Women vs North Delhi Strikers Women
# Factoring in Same Venue / Recurring Pitch Protocol (Arun Jaitley Stadium - Bowling / Pacer Friendly)
data = [
    {
        "name": "D Nagar",
        "team": "SDS-W",
        "role": "AR",
        "credits": 9.0,
        "ceiling": 145,
    },
    {
        "name": "R Beniwal",
        "team": "NDS-W",
        "role": "AR",
        "credits": 9.0,
        "ceiling": 140,
    },
    {
        "name": "Shweta Sehrawat",
        "team": "SDS-W",
        "role": "BAT",
        "credits": 9.5,
        "ceiling": 135,
    },
    {
        "name": "N Singh",
        "team": "SDS-W",
        "role": "WK",
        "credits": 8.5,
        "ceiling": 125,
    },
    {
        "name": "N Khan",
        "team": "NDS-W",
        "role": "AR",
        "credits": 8.5,
        "ceiling": 120,
    },
    {
        "name": "S Sharma",
        "team": "NDS-W",
        "role": "AR",
        "credits": 8.5,
        "ceiling": 118,
    },
    {
        "name": "P Mishra",
        "team": "NDS-W",
        "role": "BOWL",
        "credits": 8.0,
        "ceiling": 130,
    },
    {
        "name": "M Singh",
        "team": "SDS-W",
        "role": "BOWL",
        "credits": 8.0,
        "ceiling": 128,
    },
    {
        "name": "T Singh",
        "team": "SDS-W",
        "role": "AR",
        "credits": 8.0,
        "ceiling": 115,
    },
    {
        "name": "U Yadav",
        "team": "NDS-W",
        "role": "BAT",
        "credits": 7.5,
        "ceiling": 105,
    },
    {
        "name": "E Bhadana",
        "team": "SDS-W",
        "role": "BOWL",
        "credits": 7.5,
        "ceiling": 110,
    },
    {
        "name": "S Jangid",
        "team": "NDS-W",
        "role": "BOWL",
        "credits": 7.5,
        "ceiling": 102,
    },
    {
        "name": "A Anand",
        "team": "NDS-W",
        "role": "BOWL",
        "credits": 7.5,
        "ceiling": 100,
    },
    {
        "name": "P Punia",
        "team": "SDS-W",
        "role": "BAT",
        "credits": 8.0,
        "ceiling": 98,
    },
]

df = pd.DataFrame(data)

# Initialize PuLP Problem
prob = pl.LpProblem("Fantasy_Cricket_Optimization", pl.LpMaximize)

# Decision Variables
player_vars = {i: pl.LpVariable(f"player_{i}", cat="Binary") for i in df.index}

# Objective Function: Maximize Ceiling
prob += (
    pl.lpSum(df.loc[i, "ceiling"] * player_vars[i] for i in df.index),
    "Total_Ceiling",
)

# Constraints
prob += (
    pl.lpSum(player_vars[i] for i in df.index) == 11,
    "Total_Players_Constraint",
)
prob += (
    pl.lpSum(df.loc[i, "credits"] * player_vars[i] for i in df.index) <= 100.0,
    "Credit_Limit_Constraint",
)

# Role Constraints
prob += (
    pl.lpSum(player_vars[i] for i in df.index if df.loc[i, "role"] == "WK") >= 1,
    "Min_WK",
)
prob += (
    pl.lpSum(player_vars[i] for i in df.index if df.loc[i, "role"] == "WK") <= 4,
    "Max_WK",
)
prob += (
    pl.lpSum(player_vars[i] for i in df.index if df.loc[i, "role"] == "BAT")
    >= 1,
    "Min_BAT",
)
prob += (
    pl.lpSum(player_vars[i] for i in df.index if df.loc[i, "role"] == "BAT")
    <= 6,
    "Max_BAT",
)
prob += (
    pl.lpSum(path for path in [player_vars[i] for i in df.index if df.loc[i, "role"] == "AR"])  # type: ignore
    >= 1,
    "Min_AR",
)
prob += (
    pl.lpSum(player_vars[i] for i in df.index if df.loc[i, "role"] == "AR")
    <= 6,
    "Max_AR",
)
prob += (
    pl.lpSum(player_vars[i] for i in df.index if df.loc[i, "role"] == "BOWL")
    >= 1,
    "Min_BOWL",
)
prob += (
    pl.lpSum(player_vars[i] for i in df.index if df.loc[i, "role"] == "BOWL")
    <= 6,
    "Max_BOWL",
)

# Team Balance Constraints (Max 7 from one team, min 4)
teams = df["team"].unique()
for team in teams:
  prob += (
      pl.lpSum(player_vars[i] for i in df.index if df.loc[i, "team"] == team)
      <= 7,
      f"Max_Team_{team}",
  )
  prob += (
      pl.lpSum(player_vars[i] for i in df.index if df.loc[i, "team"] == team)
      >= 4,
      f"Min_Team_{team}",
  )

# Solve
prob.solve(pl.PULP_CBC_CMD(msg=False))

if pl.LpStatus[prob.status] == "Optimal":
  selected_indices = [i for i in df.index if player_vars[i].varValue == 1]
  optimal_team = df.loc[selected_indices].reset_index(drop=True)

  print("\n" + "=" * 50)
  print("SUCCESS: Optimal Lineup Generated!")
  print("=" * 50)
  print(
      f"Total Credits Used: {optimal_team['credits'].sum()} / 100.0"
  )  # type: ignore
  print(f"Projected Ceiling: {optimal_team['ceiling'].sum()} Pts\n")  # type: ignore
  print(optimal_team[["name", "team", "role", "credits", "ceiling"]])
  print("=" * 50)
else:
  print("No optimal solution found.")
