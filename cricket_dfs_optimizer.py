"""
Cricket DFS Optimizer with Captain/VC, Stacking, CSV Upload & Gemini AI review.
Uses pulp for exact optimization and OpenRouter (OX‑ALPHA) for free Gemini access.
"""

import csv
import io
import json
import os
import requests
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

from pulp import *

# ---------- OX‑ALPHA / OpenRouter Configuration ----------
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-pro"   # change to your preferred Gemini slug
API_KEY = os.getenv("OX_ALPHA_KEY", "your-ox-alpha-key")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-Title": "Cricket DFS Optimizer",
}

# ---------- Data Model ----------
@dataclass
class Player:
    name: str
    role: str       # BAT / WK / AR / BOWL
    salary: int
    points: float
    team: str

def normalize_role(raw: str) -> str:
    raw = raw.strip().upper()
    mapping = {
        "BAT": "BAT", "B": "BAT", "BATSMAN": "BAT",
        "BOWL": "BOWL", "BOWLER": "BOWL", "BOWLING": "BOWL",
        "AR": "AR", "ALL": "AR", "ALL-ROUNDER": "AR", "ALLROUNDER": "AR",
        "WK": "WK", "WKT": "WK", "KEEPER": "WK", "WICKETKEEPER": "WK",
    }
    return mapping.get(raw, "BAT")   # default to BAT if unknown

# ---------- CSV Parsing ----------
def parse_csv(text: str) -> List[Player]:
    """
    Handles DraftKings/FanDuel style cricket CSVs.
    Expected columns: Position, Name, Salary, Team, AvgPointsPerGame (or similar).
    We auto‑detect by header.
    """
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV has no header row")

    # Normalize header names
    headers = {h.strip().lower(): h for h in reader.fieldnames}

    # Required columns (with synonyms)
    def find_col(*names):
        for n in names:
            if n in headers:
                return headers[n]
        return None

    col_pos = find_col("position", "pos", "role")
    col_name = find_col("name", "player", "playername")
    col_sal = find_col("salary", "price")
    col_pts = find_col("avgpointspergame", "points", "projection", "fpts", "fantasypoints")
    col_team = find_col("team", "teamabbrev")

    if not (col_name and col_sal and col_pts):
        raise ValueError("CSV missing Name, Salary, or Points column")

    players = []
    for row in reader:
        name = row[col_name].strip()
        if not name:
            continue

        salary = int(float(row[col_sal]))
        points = float(row[col_pts])
        team = row.get(col_team, "UNK").strip() if col_team else "UNK"
        role = normalize_role(row.get(col_pos, "BAT")) if col_pos else "BAT"

        players.append(Player(name=name, role=role, salary=salary, points=points, team=team))

    if not players:
        raise ValueError("No player rows found")
    return players

# ---------- Optimizer ----------
def optimize_lineup(
    players: List[Player],
    salary_cap: int = 100000,
    team_size: int = 11,
    role_min: Dict[str, int] = None,
    role_max: Dict[str, int] = None,
    max_per_team: int = 7,
    captain_mult: float = 2.0,
    vice_mult: float = 1.5,
) -> Tuple[List[Tuple[Player, str]], float]:
    """
    Returns (lineup, total_points).
    Lineup is list of (player, designation) where designation in {'', 'C', 'VC'}.
    """
    if role_min is None:
        role_min = {"BAT": 3, "WK": 1, "AR": 2, "BOWL": 3}
    if role_max is None:
        role_max = {"BAT": 5, "WK": 2, "AR": 4, "BOWL": 5}

    n = len(players)
    x = LpVariable.dicts("x", range(n), cat="Binary")         # in lineup
    c = LpVariable.dicts("c", range(n), cat="Binary")         # captain
    v = LpVariable.dicts("v", range(n), cat="Binary")         # vice captain

    prob = LpProblem("Cricket_DFS", LpMaximize)

    # Objective: base points + (mult-1) * cap points + (mult-1) * vc points
    prob += (
        lpSum(x[i] * players[i].points for i in range(n))
        + lpSum(c[i] * players[i].points * (captain_mult - 1) for i in range(n))
        + lpSum(v[i] * players[i].points * (vice_mult - 1) for i in range(n))
    )

    # Salary & size
    prob += lpSum(x[i] * players[i].salary for i in range(n)) <= salary_cap
    prob += lpSum(x[i] for i in range(n)) == team_size

    # Exactly one C and one VC
    prob += lpSum(c[i] for i in range(n)) == 1
    prob += lpSum(v[i] for i in range(n)) == 1

    # C/VC must be in lineup and distinct
    for i in range(n):
        prob += c[i] <= x[i]
        prob += v[i] <= x[i]
        prob += c[i] + v[i] <= 1

    # Role constraints
    for role in role_min:
        idxs = [i for i, p in enumerate(players) if p.role == role]
        prob += lpSum(x[i] for i in idxs) >= role_min.get(role, 0)
    for role in role_max:
        idxs = [i for i, p in enumerate(players) if p.role == role]
        prob += lpSum(x[i] for i in idxs) <= role_max.get(role, team_size)

    # Team stacking
    teams = set(p.team for p in players)
    for team in teams:
        idxs = [i for i, p in enumerate(players) if p.team == team]
        prob += lpSum(x[i] for i in idxs) <= max_per_team

    # Solve
    prob.solve(PULP_CBC_MSG(msg=0))
    if LpStatus[prob.status] != "Optimal":
        return [], 0.0

    lineup = []
    total = 0.0
    for i in range(n):
        if value(x[i]) == 1:
            designation = ""
            if value(c[i]) == 1:
                designation = "C"
            elif value(v[i]) == 1:
                designation = "VC"
            lineup.append((players[i], designation))
            total += players[i].points
            if designation == "C":
                total += players[i].points * (captain_mult - 1)
            elif designation == "VC":
                total += players[i].points * (vice_mult - 1)
    return lineup, total

# ---------- Gemini Analysis ----------
def gemini_review(lineup: List[Tuple[Player, str]], total_points: float) -> str:
    if not API_KEY or API_KEY == "your-ox-alpha-key":
        return "⚠️ Set OX_ALPHA_KEY env variable to enable Gemini analysis."

    lines = []
    for player, desig in lineup:
        stars = {"C": " (C)", "VC": " (VC)", "": ""}[desig]
        lines.append(f"{player.name} ({player.role}, {player.team}, ${player.salary}, {player.points:.1f} pts){stars}")
    lineup_text = "\n".join(lines)

    prompt = f"""You are a cricket fantasy expert. Analyze this lineup:

{lineup_text}
Total projected points (with multipliers): {total_points:.1f}

Rules: Exactly 11 players, roles: at least 3 BAT, 1 WK, 2 AR, 3 BOWL. Captain (x2), Vice-captain (x1.5).

Provide:
1. Strengths (one or two sentences).
2. Most vulnerable spot (position/player).
3. One specific player swap you'd consider (name, team, and why).
4. Is the captain choice optimal? If not, who would you captain and why?
Keep it concise — bullets are fine.
"""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        resp = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Gemini review failed: {e}"

# ---------- Main Entry ----------
def main():
    print("🏏 Cricket DFS Optimizer")
    csv_path = input("Path to player CSV: ").strip().strip('"')
    if not os.path.exists(csv_path):
        print("File not found.")
        return

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        text = f.read()

    try:
        players = parse_csv(text)
    except Exception as e:
        print(f"CSV parse error: {e}")
        return

    print(f"Loaded {len(players)} players.")

    salary_cap = int(input("Salary cap [100000]: ") or 100000)
    team_size = int(input("Team size [11]: ") or 11)
    max_team = int(input("Max players per team [7]: ") or 7)

    lineup, total = optimize_lineup(
        players, salary_cap=salary_cap, team_size=team_size, max_per_team=max_team
    )

    if not lineup:
        print("No optimal lineup found — relax constraints.")
        return

    print("\n--- Optimal Lineup ---")
    salary_used = sum(p.salary for p, _ in lineup)
    for p, desig in lineup:
        stars = {"C": " [C]", "VC": " [VC]"}.get(desig, "")
        print(f"{p.name:25s} {p.role:5s} {p.team:5s} ${p.salary:6,} {p.points:6.1f}{stars}")
    print(f"\nTotal salary: ${salary_used:,} / ${salary_cap:,}")
    print(f"Total projected: {total:.1f} pts")

    print("\n--- Gemini Review ---")
    print(gemini_review(lineup, total))

if __name__ == "__main__":
    main()
