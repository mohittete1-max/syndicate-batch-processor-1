import pandas as pd
from pulp import *

# Confirmed 22 Playing XI from Dream11 Screen
players_data = [
    # Belfast Wolves (BWV) - Batting 1st
    {
        "name": "L Tucker",
        "team": "BWV",
        "role": "WK",
        "credits": 8.0,
        "ev": 44.0,
    },
    {
        "name": "D Conway",
        "team": "BWV",
        "role": "BAT",
        "credits": 8.5,
        "ev": 48.0,
    },
    {
        "name": "P Stirling",
        "team": "BWV",
        "role": "BAT",
        "credits": 8.0,
        "ev": 42.0,
    },
    {
        "name": "T Tector",
        "team": "BWV",
        "role": "BAT",
        "credits": 8.0,
        "ev": 30.0,
    },
    {
        "name": "G Maxwell",
        "team": "BWV",
        "role": "AR",
        "credits": 9.0,
        "ev": 82.0,
    },  # Anchor
    {
        "name": "M Adair",
        "team": "BWV",
        "role": "AR",
        "credits": 8.5,
        "ev": 54.0,
    },
    {
        "name": "M Chapman",
        "team": "BWV",
        "role": "AR",
        "credits": 8.5,
        "ev": 46.0,
    },
    {
        "name": "C Jordan",
        "team": "BWV",
        "role": "BOWL",
        "credits": 8.5,
        "ev": 52.0,
    },
    {
        "name": "S Netravalkar",
        "team": "BWV",
        "role": "BOWL",
        "credits": 8.5,
        "ev": 42.0,
    },
    {
        "name": "F Klaassen",
        "team": "BWV",
        "role": "BOWL",
        "credits": 8.0,
        "ev": 32.0,
    },
    {
        "name": "M Humphreys",
        "team": "BWV",
        "role": "BOWL",
        "credits": 8.0,
        "ev": 26.0,
    },
    # Dublin Guardians (DNG) - Bowling 1st
    {
        "name": "B Calitz",
        "team": "DNG",
        "role": "WK",
        "credits": 8.0,
        "ev": 28.0,
    },
    {
        "name": "W Muhammad",
        "team": "DNG",
        "role": "BAT",
        "credits": 8.0,
        "ev": 38.0,
    },
    {
        "name": "S Krishnamurthi",
        "team": "DNG",
        "role": "BAT",
        "credits": 7.5,
        "ev": 26.0,
    },
    {
        "name": "H Tector",
        "team": "DNG",
        "role": "AR",
        "credits": 8.0,
        "ev": 76.0,
    },  # Anchor
    {
        "name": "D Mitchell",
        "team": "DNG",
        "role": "AR",
        "credits": 8.5,
        "ev": 50.0,
    },
    {
        "name": "V Shankar",
        "team": "DNG",
        "role": "AR",
        "credits": 7.5,
        "ev": 48.0,
    },
    {
        "name": "G Dockrell",
        "team": "DNG",
        "role": "AR",
        "credits": 8.0,
        "ev": 36.0,
    },
    {
        "name": "R Ashwin",
        "team": "DNG",
        "role": "BOWL",
        "credits": 9.0,
        "ev": 66.0,
    },  # Anchor
    {
        "name": "J Little",
        "team": "DNG",
        "role": "BOWL",
        "credits": 8.5,
        "ev": 50.0,
    },
    {
        "name": "C Wood",
        "team": "DNG",
        "role": "BOWL",
        "credits": 8.0,
        "ev": 44.0,
    },
    {
        "name": "M Hollard",
        "team": "DNG",
        "role": "BOWL",
        "credits": 7.0,
        "ev": 26.0,
    },
]


def solve_lineup(players):
    prob = LpProblem("DFS_Optimizer", LpMaximize)
    player_vars = {
        p["name"]: LpVariable(f"p_{i}", cat="Binary")
        for i, p in enumerate(players)
    }

    # Objective: Maximize EV
    prob += lpSum(
        [player_vars[p["name"]] * p["ev"] for p in players]
    ), "Total_EV"

    # Constraints
    prob += (
        lpSum([player_vars[p["name"]] for p in players]) == 11,
        "Total_11_Players",
    )
    prob += (
        lpSum([player_vars[p["name"]] * p["credits"] for p in players])
        <= 100.0,
        "Max_Credits",
    )

    # Team Limits (max 7 from one team)
    prob += (
        lpSum(
            [player_vars[p["name"]] for p in players if p["team"] == "BWV"]
        )
        <= 7,
        "BWV_Limit",
    )
    prob += (
        lpSum(
            [player_vars[p["name"]] for p in players if p["team"] == "DNG"]
        )
        <= 7,
        "DNG_Limit",
    )

    # Role Constraints
    prob += (
        lpSum([player_vars[p["name"]] for p in players if p["role"] == "WK"])
        >= 1,
        "Min_WK",
    )
    prob += (
        lpSum([player_vars[p["name"]] for p in players if p["role"] == "BAT"])
        >= 2,
        "Min_BAT",
    )
    prob += (
        lpSum([player_vars[p["name"]] for p in players if p["role"] == "AR"])
        >= 3,
        "Min_AR",
    )
    prob += (
        lpSum([player_vars[p["name"]] for p in players if p["role"] == "BOWL"])
        >= 2,
        "Min_BOWL",
    )

    prob.solve(PULP_CBC_CMD(msg=0))

    selected = [p for p in players if player_vars[p["name"]].varValue == 1]
    return pd.DataFrame(selected)


if __name__ == "__main__":
    team = solve_lineup(players_data)
    print("=== OPTIMAL SOLVED LINEUP ===")
    print(
        team[["name", "team", "role", "credits", "ev"]].to_string(index=False)
    )
    print(f"\nTotal Credits: {team['credits'].sum()} / 100.0")
    print(f"Total Projected EV: {team['ev'].sum()}")
