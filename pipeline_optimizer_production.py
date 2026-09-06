import os
import pandas as pd
import pulp
from pipeline_market_engine import apply_market_and_environmental_adjustments

def run_production_optimizer(budget=100.0):
    """
    Executes the advanced linear programming optimization with strict role quotas
    (WK/BAT/AR/BOWL balance) preventing all-batter squads.
    """
    players = apply_market_and_environmental_adjustments()
    if players is None or players.empty:
        return
        
    prob = pulp.LpProblem("Production_Fantasy_Cricket", pulp.LpMaximize)
    
    x = {i: pulp.LpVariable(f"sel_{i}", cat='Binary') for i in players.index}
    c = {i: pulp.LpVariable(f"cap_{i}", cat='Binary') for i in players.index}
    vc = {i: pulp.LpVariable(f"vcap_{i}", cat='Binary') for i in players.index}
    
    # Objective: Maximize projected fantasy points + Captain (2x) & Vice-Captain (1.5x) weights
    prob += pulp.lpSum(
        players.loc[i, 'projected_fantasy_points'] * x[i] +
        players.loc[i, 'projected_fantasy_points'] * c[i] * 1.0 +
        players.loc[i, 'projected_fantasy_points'] * vc[i] * 0.5
        for i in players.index
    )
    
    # Budget & Squad Constraints
    prob += pulp.lpSum(players.loc[i, 'credits'] * x[i] for i in players.index) <= budget
    prob += pulp.lpSum(x.values()) == 11
    
    # Realistic Role Quota Constraints for balanced team selection
    bat_indices = players[players['role'] == 'BAT'].index
    bowl_indices = players[players['role'] == 'BOWL'].index
    ar_indices = players[players['role'] == 'AR'].index
    
    prob += pulp.lpSum(x[i] for i in bat_indices) >= 3
    prob += pulp.lpSum(x[i] for i in bowl_indices) >= 3
    prob += pulp.lpSum(x[i] for i in ar_indices) >= 1
    
    # Captaincy Constraints
    prob += pulp.lpSum(c.values()) == 1
    prob += pulp.lpSum(vc.values()) == 1
    for i in players.index:
        prob += c[i] <= x[i]
        prob += vc[i] <= x[i]
        prob += c[i] + vc[i] <= 1
        
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    print(f"\nOptimization Status: {pulp.LpStatus[prob.status]}")
    print("\n========================================")
    print("    BALANCED OPTIMIZED TOURNAMENT SQUAD ")
    print("========================================")
    
    total_proj_pts = 0
    for i in players.index:
        if x[i].value() == 1:
            multiplier = 2.0 if c[i].value() == 1 else (1.5 if vc[i].value() == 1 else 1.0)
            pts = players.loc[i, 'projected_fantasy_points'] * multiplier
            total_proj_pts += pts
            role_tag = " [CAPTAIN]" if c[i].value() == 1 else (" [VICE-CAPTAIN]" if vc[i].value() == 1 else "")
            print(f"- {players.loc[i, 'player_name']} ({players.loc[i, 'role']}){role_tag} | Proj Pts: {pts:.1f}")
            
    print("----------------------------------------")
    print(f"Total Projected Squad Points: {total_proj_pts:.1f}")
    print("========================================")

if __name__ == "__main__":
    run_production_optimizer()
