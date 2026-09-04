# gpp_engine.py
import pandas as pd
import pulp
import scraper

def generate_gpp_portfolios(num_lineups=5):
    """
    Generates multi-entry GPP portfolios with ownership leverage weights 
    and mandatory dissimilarity constraints between entries.
    """
    print("GPP Engine: Initializing Grand League differentiation matrix...")
    live_data = scraper.fetch_live_stats()
    
    # Simulated ownership percentage metrics (in production, loaded from contest data pools)
    live_data['Ownership'] = [15.0, 28.0, 55.0, 42.0, 31.0, 9.5, 12.0, 24.0, 7.5, 19.0, 13.5, 21.0, 26.0]
    
    indices = live_data.index.tolist()
    previous_lineups = []
    gpp_portfolios = []
    
    for l_num in range(1, num_lineups + 1):
        prob = pulp.LpProblem(f"GPP_Lineup_{l_num}", pulp.LpMaximize)
        
        p_vars = pulp.LpVariable.dicts(f"Sel_{l_num}", indices, cat='Binary')
        c_vars = pulp.LpVariable.dicts(f"Cap_{l_num}", indices, cat='Binary')
        vc_vars = pulp.LpVariable.dicts(f"VCap_{l_num}", indices, cat='Binary')
        
        # Objective Function: Maximize Points with Contrarian Ownership Boosts (< 15% ownership)
        objective_expr = []
        for i in indices:
            pts = live_data['Points'][i]
            own = live_data['Ownership'][i]
            
            # Low ownership differential factor for GPP leverage
            leverage_factor = 1.15 if own < 15.0 else 1.0
            eff_pts = pts * leverage_factor
            
            objective_expr.append(
                eff_pts * p_vars[i] + 
                eff_pts * c_vars[i] + 
                (0.5 * eff_pts) * vc_vars[i]
            )
            
        prob += pulp.lpSum(objective_expr)
        
        # Core Constraints
        prob += pulp.lpSum([p_vars[i] for i in indices]) == 11
        prob += pulp.lpSum([live_data['Credits'][i] * p_vars[i] for i in indices]) <= 100.0
        prob += pulp.lpSum([c_vars[i] for i in indices]) == 1
        prob += pulp.lpSum([vc_vars[i] for i in indices]) == 1
        
        for i in indices:
            prob += c_vars[i] <= p_vars[i]
            prob += vc_vars[i] <= p_vars[i]
            prob += c_vars[i] + vc_vars[i] <= 1
            
        # Dissimilarity / Uniqueness Constraint: 
        # Ensures each subsequent lineup differs by at least 3 players from prior lineups
        for prev_idx, prev_players in enumerate(previous_lineups):
            prob += pulp.lpSum([p_vars[i] for i in prev_players]) <= 8, f"Dissimilarity_{prev_idx}_{l_num}"
            
        prob.solve()
        
        if pulp.LpStatus[prob.status] == 'Optimal':
            current_lineup_indices = []
            lineup_summary = []
            
            for i in indices:
                if p_vars[i].varValue == 1.0:
                    current_lineup_indices.append(i)
                    lineup_summary.append(f"[{live_data['Role'][i]}] {live_data['Player'][i]}")
                    
            previous_lineups.append(current_lineup_indices)
            gpp_portfolios.append({
                "Lineup_ID": f"GPP_Matrix_{l_num}",
                "Roster": ", ".join(lineup_summary)
            })
            print(f"GPP Lineup {l_num} generated successfully with unique differentiation.")
        else:
            print(f"GPP Lineup {l_num} optimization failed.")
            
    return pd.DataFrame(gpp_portfolios)

if __name__ == "__main__":
    df_gpp = generate_gpp_portfolios(3)
    print(df_gpp)
