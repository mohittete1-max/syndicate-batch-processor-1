import pandas as pd
import pulp

def run_ultimate_h2h_engine():
    try:
        df = pd.read_csv("match_squad_data.csv")
        
        # Standardize projection columns
        if "projected" in df.columns and "projected_points" not in df.columns:
            df["projected_points"] = df["projected"]
        elif "projected_points" in df.columns and "projected" not in df.columns:
            df["projected"] = df["projected_points"]

        if "ceiling_ev" not in df.columns:
            df["ceiling_ev"] = df["projected_points"] * 1.15
        if "differential_bonus" not in df.columns:
            df["differential_bonus"] = 0.0

        # Post-Toss Lineup Validation (Defaults to 1 if pre-toss)
        if "is_playing" not in df.columns:
            df["is_playing"] = 1
        else:
            df["is_playing"] = pd.to_numeric(df["is_playing"], errors='coerce').fillna(1).astype(int)

        # 1. Define Optimization Problem
        prob = pulp.LpProblem("Ultimate_H2H_Engine", pulp.LpMaximize)
        
        x = pulp.LpVariable.dicts("drafted", df.index, cat='Binary')
        c = pulp.LpVariable.dicts("captain", df.index, cat='Binary')
        v = pulp.LpVariable.dicts("vice_captain", df.index, cat='Binary')
        
        # 2. Hybrid Objective Function (70% Median / 30% Ceiling)
        prob += pulp.lpSum([
            (0.7 * df.loc[i, 'projected_points'] + 0.3 * df.loc[i, 'ceiling_ev'] + df.loc[i, 'differential_bonus']) * x[i] + 
            (0.7 * df.loc[i, 'projected_points'] + 0.3 * df.loc[i, 'ceiling_ev']) * 1.0 * c[i] + 
            (0.7 * df.loc[i, 'projected_points'] + 0.3 * df.loc[i, 'ceiling_ev']) * 0.5 * v[i] 
            for i in df.index
        ])
        
        # 3. Mathematical Constraints
        prob += pulp.lpSum([x[i] for i in df.index]) == 11
        prob += pulp.lpSum([df.loc[i, 'credits'] * x[i] for i in df.index]) <= 100.0
        prob += pulp.lpSum([c[i] for i in df.index]) == 1
        prob += pulp.lpSum([v[i] for i in df.index]) == 1
        
        for i in df.index:
            prob += c[i] <= x[i]
            prob += v[i] <= x[i]
            prob += c[i] + v[i] <= 1
            
            # Post-Toss Exclusion Lock
            if df.loc[i, 'is_playing'] == 0:
                prob += x[i] == 0
            
            # Multiplier Lock (AR & BOWL only)
            if df.loc[i, 'role'] not in ['AR', 'BOWL']:
                prob += c[i] == 0
                prob += v[i] == 0

        # Positional Caps
        prob += pulp.lpSum([x[i] for i in df.index if df.loc[i, 'role'] == 'WK']) == 1
        prob += pulp.lpSum([x[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) >= 1
        prob += pulp.lpSum([x[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) <= 2
        prob += pulp.lpSum([x[i] for i in df.index if df.loc[i, 'role'] == 'AR']) >= 1
        prob += pulp.lpSum([x[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) >= 1
        
        # 4. Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        
        if pulp.LpStatus[prob.status] != 'Optimal':
            print("[ERROR] Solver failed. Verify that at least 11 active players meet roster constraints.")
            return
            
        selected_indices = [i for i in df.index if x[i].varValue == 1.0]
        lineup_df = df.loc[selected_indices].copy()
        
        lineup_df['Multiplier_Tag'] = 'Base'
        for i in selected_indices:
            if c[i].varValue == 1.0:
                lineup_df.at[i, 'Multiplier_Tag'] = 'Captain (2x)'
            elif v[i].varValue == 1.0:
                lineup_df.at[i, 'Multiplier_Tag'] = 'Vice-Captain (1.5x)'
                
        total_ev = pulp.value(prob.objective)
        total_creds = lineup_df['credits'].sum()
        
        lineup_df.to_csv("Team_1_H2H_Cash.csv", index=False)
        print(f"[ULTIMATE SUCCESS] H2H Hybrid Lineup Generated | Combined Score: {total_ev:.2f} | Credits: {total_creds:.1f}/100")
        
    except Exception as e:
        print(f"[CRITICAL EXCEPTION] {e}")

if __name__ == "__main__":
    run_ultimate_h2h_engine()
