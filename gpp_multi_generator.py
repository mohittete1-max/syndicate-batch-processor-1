import pulp
import pandas as pd
import os

def generate_gpp_portfolio():
    input_file = "weather_and_vegas_adjusted_slate.csv"
    output_file = "fully_compounded_gpp_portfolio.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Run weather and Vegas integrators first.")
        return

    df = pd.read_csv(input_file)
    print(f"Loading market and weather adjusted projections from: {input_file}")
    
    players = df['player'].tolist()
    teams = df['team'].tolist()
    roles = df['role'].tolist()
    salaries = df['salary'].tolist()
    projections = df['projected_points'].tolist()
    
    n_lineups = 20
    max_overlap = 8
    portfolio_results = []
    previous_lineups_indices = []

    for l_idx in range(1, n_lineups + 1):
        prob = pulp.LpProblem(f"GPP_Lineup_{l_idx}", pulp.LpMaximize)
        
        x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(len(players))}
        c = {i: pulp.LpVariable(f"c_{i}", cat="Binary") for i in range(len(players))}
        vc = {i: pulp.LpVariable(f"vc_{i}", cat="Binary") for i in range(len(players))}
        
        prob += pulp.lpSum(x[i] * projections[i] + c[i] * projections[i] + vc[i] * (projections[i] * 0.5) for i in range(len(players)))
        
        prob += pulp.lpSum(x[i] for i in range(len(players))) == 11
        prob += pulp.lpSum(x[i] * salaries[i] for i in range(len(players))) <= 100.0
        
        prob += pulp.lpSum(c[i] for i in range(len(players))) == 1
        prob += pulp.lpSum(vc[i] for i in range(len(players))) == 1
        
        for i in range(len(players)):
            prob += c[i] <= x[i]
            prob += vc[i] <= x[i]
            prob += c[i] + vc[i] <= 1
            
        wk_indices = [i for i, r in enumerate(roles) if r == 'WK']
        bat_indices = [i for i, r in enumerate(roles) if r == 'BAT']
        ar_indices = [i for i, r in enumerate(roles) if r == 'AR']
        bowl_indices = [i for i, r in enumerate(roles) if r == 'BOWL']
        
        if wk_indices:
            prob += pulp.lpSum(x[i] for i in wk_indices) >= 1
            prob += pulp.lpSum(x[i] for i in wk_indices) <= 4
        if bat_indices:
            prob += pulp.lpSum(x[i] for i in bat_indices) >= 1
            prob += pulp.lpSum(x[i] for i in bat_indices) <= 6
        if ar_indices:
            prob += pulp.lpSum(x[i] for i in ar_indices) >= 1
            prob += pulp.lpSum(x[i] for i in ar_indices) <= 6
        if bowl_indices:
            prob += pulp.lpSum(x[i] for i in bowl_indices) >= 1
            prob += pulp.lpSum(x[i] for i in bowl_indices) <= 6
            
        unique_teams = list(set(teams))
        for t in unique_teams:
            t_indices = [i for i, team in enumerate(teams) if team == t]
            prob += pulp.lpSum(x[i] for i in t_indices) <= 7
            
        for prev_indices in previous_lineups_indices:
            prob += pulp.lpSum(x[i] for i in prev_indices) <= max_overlap
            
        prob.solve(pulp.PULP_CBC_CMD(msg=False))
        
        if pulp.LpStatus[prob.status] != 'Optimal':
            print(f"Warning: Lineup {l_idx} did not yield an optimal solution. Status: {prob.status}")
            break
            
        current_indices = [i for i in range(len(players)) if pulp.value(x[i]) > 0.5]
        previous_lineups_indices.append(current_indices)
        
        c_player_idx = next(i for i in range(len(players)) if pulp.value(c[i]) > 0.5)
        vc_player_idx = next(i for i in range(len(players)) if pulp.value(vc[i]) > 0.5)
        
        total_proj = sum(projections[i] for i in current_indices) + projections[c_player_idx] + (projections[vc_player_idx] * 0.5)
        total_salary = sum(salaries[i] for i in current_indices)
        
        c_name = players[c_player_idx]
        vc_name = players[vc_player_idx]
        
        print(f"Lineup {l_idx:02d} | Proj: {total_proj:.2f} | Salary: {total_salary:.1f}/100 | (C): {c_name} | (VC): {vc_name}")
        
        for i in current_indices:
            tag = ""
            if i == c_player_idx:
                tag = "(C)"
            elif i == vc_player_idx:
                tag = "(VC)"
            portfolio_results.append({
                "lineup_id": l_idx,
                "player": players[i],
                "team": teams[i],
                "role": roles[i],
                "salary": salaries[i],
                "projected_points": projections[i],
                "tag": tag,
                "total_lineup_projection": round(total_proj, 2)
            })

    portfolio_df = pd.DataFrame(portfolio_results)
    portfolio_df.to_csv(output_file, index=False)
    print(f"\nPortfolio Complete: 20 fully compounded lineups exported to '{output_file}'.")

if __name__ == "__main__":
    generate_gpp_portfolio()
