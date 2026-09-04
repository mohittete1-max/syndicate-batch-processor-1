import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pulp

# Set Streamlit Page Configuration
st.set_page_config(page_title="Apex Alpha OS: Market Odds Syndicate", layout="wide")

st.title("🌍 Apex Alpha OS: 4-Layer Grand League Engine")
st.markdown("Live Market Odds Injection | Game Theory | Post-Toss Late Swap")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Match & Portfolio Setup")
tournament = st.sidebar.selectbox("Tournament", ["Delhi Premier League 2026", "CPL", "IPL"])
match_name = st.sidebar.text_input("Fixture", "ODW vs EDR")
team_count = st.sidebar.slider("Portfolios to Generate", min_value=5, max_value=30, value=15)
investment = st.sidebar.number_input("Total Investment (INR)", value=735.0)

st.sidebar.subheader("🚀 Volatility Tuning ($k$)")
k_multiplier = st.sidebar.slider("Grand League Upside Multiplier (k)", 1.0, 2.5, 1.5, 0.1)

# --- 📈 MARKET ODDS INJECTION CONTROLS ---
st.sidebar.subheader("📈 Implied Market Odds (Vegas Lines)")
st.caption("Adjust base projections dynamically using live betting market totals.")
odw_implied_total = st.sidebar.number_input("ODW Implied Run Total", value=195.5, step=1.0)
edr_implied_total = st.sidebar.number_input("EDR Implied Run Total", value=160.5, step=1.0)
odw_win_prob = st.sidebar.slider("ODW Win Probability (%)", 0, 100, 68)

# --- ⚡ LATE-SWAP CONTROLS ---
st.sidebar.subheader("⚡ Post-Toss Late Swap")
toss_winner = st.sidebar.selectbox("Toss Won By", ["Outer Delhi Warriors", "East Delhi Riders"])
toss_decision = st.sidebar.radio("Toss Decision", ["Bowl First (Chasing)", "Bat First (Defending)"])

st.sidebar.subheader("🎛️ Role Constraints")
min_wk = st.sidebar.slider("Min Wicket-Keepers (WK)", 1, 3, 1)
max_wk = st.sidebar.slider("Max Wicket-Keepers (WK)", 1, 4, 2)
min_bat = st.sidebar.slider("Min Batters (BAT)", 1, 6, 3)
max_bat = st.sidebar.slider("Max Batters (BAT)", 3, 6, 5)
min_ar = st.sidebar.slider("Min All-Rounders (AR)", 1, 6, 2)
max_ar = st.sidebar.slider("Max All-Rounders (AR)", 1, 6, 4)
min_bowl = st.sidebar.slider("Min Bowlers (Pace + Spin)", 3, 7, 3)
max_bowl = st.sidebar.slider("Max Bowlers (Pace + Spin)", 3, 7, 5)

# --- FULL SQUAD DATABASE ---
def get_master_pool():
    data = [
        # Outer Delhi Warriors (ODW)
        {"name": "Yajas Sharma", "role": "BAT", "team": "ODW", "credits": 9.5, "base_pts": 85.0, "sigma": 30.0, "top_order_bat": 1, "death_overs": 0},
        {"name": "Priyansh Arya", "role": "BAT", "team": "ODW", "credits": 9.0, "base_pts": 78.0, "sigma": 25.0, "top_order_bat": 1, "death_overs": 0},
        {"name": "Dhruv Singh", "role": "WK", "team": "ODW", "credits": 8.5, "base_pts": 65.0, "sigma": 20.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Siddhant Sharma", "role": "AR", "team": "ODW", "credits": 9.0, "base_pts": 70.0, "sigma": 22.0, "top_order_bat": 0, "death_overs": 1},
        {"name": "Navdeep Saini", "role": "PACE", "team": "ODW", "credits": 9.5, "base_pts": 76.0, "sigma": 26.0, "top_order_bat": 0, "death_overs": 1},
        {"name": "Harsh Tyagi", "role": "SPIN", "team": "ODW", "credits": 8.5, "base_pts": 74.0, "sigma": 24.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Akshay Saini", "role": "AR", "team": "ODW", "credits": 8.0, "base_pts": 55.0, "sigma": 18.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Monu Shukla", "role": "PACE", "team": "ODW", "credits": 8.0, "base_pts": 52.0, "sigma": 16.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Shivam Sharma", "role": "SPIN", "team": "ODW", "credits": 8.0, "base_pts": 50.0, "sigma": 15.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Pratham Saluja", "role": "AR", "team": "ODW", "credits": 8.5, "base_pts": 60.0, "sigma": 20.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Varun Yadav", "role": "BAT", "team": "ODW", "credits": 8.0, "base_pts": 58.0, "sigma": 18.0, "top_order_bat": 0, "death_overs": 0},

        # East Delhi Riders (EDR)
        {"name": "Arpit Rana", "role": "BAT", "team": "EDR", "credits": 9.5, "base_pts": 80.0, "sigma": 28.0, "top_order_bat": 1, "death_overs": 0},
        {"name": "Vansh Mehra", "role": "BAT", "team": "EDR", "credits": 8.5, "base_pts": 68.0, "sigma": 22.0, "top_order_bat": 1, "death_overs": 0},
        {"name": "Suryansh Raina", "role": "WK", "team": "EDR", "credits": 8.5, "base_pts": 65.0, "sigma": 20.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Simarjeet Singh", "role": "PACE", "team": "EDR", "credits": 9.0, "base_pts": 72.0, "sigma": 25.0, "top_order_bat": 0, "death_overs": 1},
        {"name": "Mayank Yadav", "role": "PACE", "team": "EDR", "credits": 9.0, "base_pts": 75.0, "sigma": 28.0, "top_order_bat": 0, "death_overs": 1},
        {"name": "Ashish Meena", "role": "PACE", "team": "EDR", "credits": 8.5, "base_pts": 70.0, "sigma": 24.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Mayank Rawat", "role": "AR", "team": "EDR", "credits": 8.5, "base_pts": 64.0, "sigma": 21.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Sujal Singh", "role": "BAT", "team": "EDR", "credits": 8.0, "base_pts": 55.0, "sigma": 18.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Vaibhav Baisla", "role": "AR", "team": "EDR", "credits": 8.0, "base_pts": 50.0, "sigma": 15.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Yashwardhan Oberai", "role": "AR", "team": "EDR", "credits": 8.0, "base_pts": 52.0, "sigma": 16.0, "top_order_bat": 0, "death_overs": 0},
        {"name": "Deepak Punia", "role": "SPIN", "team": "EDR", "credits": 8.0, "base_pts": 48.0, "sigma": 14.0, "top_order_bat": 0, "death_overs": 0},
    ]
    return pd.DataFrame(data)

master_df = get_master_pool()

# --- 📋 POST-TOSS ACTIVE XI FILTER ---
st.subheader("📋 Step 1: Confirm Playing XI")
all_players = master_df["name"].tolist()
confirmed_xi = st.multiselect("Uncheck benched players:", options=all_players, default=all_players)
active_df = master_df[master_df["name"].isin(confirmed_xi)].copy().reset_index(drop=True)

# --- 🎯 THE MARKET ODDS INJECTION PROTOCOL ---
# 1. High Implied Total Boost (Scales Top Order Base Points)
if odw_implied_total >= 185.0:
    active_df.loc[(active_df["team"] == "ODW") & (active_df["top_order_bat"] == 1), "base_pts"] += ((odw_implied_total - 185) * 0.4)
if edr_implied_total >= 185.0:
    active_df.loc[(active_df["team"] == "EDR") & (active_df["top_order_bat"] == 1), "base_pts"] += ((edr_implied_total - 185) * 0.4)

# 2. Low Implied Total Penalty (Boosts Opposing Death Bowlers)
if edr_implied_total <= 165.0:
    active_df.loc[(active_df["team"] == "EDR") & (active_df["top_order_bat"] == 1), "base_pts"] -= 4.0
    active_df.loc[(active_df["team"] == "ODW") & (active_df["death_overs"] == 1), "base_pts"] += 7.0

# 3. Win Probability Volatility Injector (Scales Bowler Sigma for Heavy Favorites)
if odw_win_prob > 65:
    active_df.loc[(active_df["team"] == "ODW") & (active_df["role"].isin(["PACE", "SPIN"])), "sigma"] += 4.5
elif odw_win_prob < 40:
    active_df.loc[(active_df["team"] == "EDR") & (active_df["role"].isin(["PACE", "SPIN"])), "sigma"] += 4.5

# Calculate the final Opportunity-Weighted Ceiling
active_df["opportunity_score"] = (active_df["death_overs"] * 14.0) + (active_df["top_order_bat"] * 11.0) + (active_df["base_pts"] * 0.2)
active_df["projected_ceiling"] = active_df["base_pts"] + (k_multiplier * (active_df["sigma"] + (active_df["opportunity_score"] * 0.45)))

# --- 📊 LIVE POST-TOSS PLOTLY MATRIX ---
st.subheader("📊 Step 2: Market-Adjusted Ceiling Matrix")
fig = px.scatter(
    active_df, x="credits", y="projected_ceiling", size="opportunity_score", color="role",
    hover_name="name", text="name",
    title=f"Odds-Injected Matrix | ODW Line: {odw_implied_total} | EDR Line: {edr_implied_total}"
)
fig.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="DarkSlateGrey")))
fig.update_layout(xaxis_title="Dream11 Credits", yaxis_title="Recalibrated 90th-Percentile Ceiling", hovermode="closest")
st.plotly_chart(fig, use_container_width=True)

# --- 🚀 RAPID OPTIMIZER ---
st.subheader("🚀 Step 3: Syndicate Generation")
locked_players = st.text_input("Lock Players (Must be active)", "Yajas Sharma")
run_optimizer = st.button("⚡ Execute Market-Weighted Optimization", type="primary")

if run_optimizer:
    if len(active_df) < 11:
        st.error("Cannot optimize: fewer than 11 confirmed players selected.")
    else:
        locked_list = [p.strip() for p in locked_players.split(",") if p.strip() in active_df["name"].values]
        portfolios, penalty_tracker = [], {i: 0 for i in active_df.index}
        
        for t in range(int(team_count)):
            active_df["simulated_ceiling"] = active_df["projected_ceiling"] * np.random.uniform(0.92, 1.08, len(active_df))
            prob = pulp.LpProblem(f"Market_Team_{t}", pulp.LpMaximize)
            vars = pulp.LpVariable.dicts("P", active_df.index, cat=pulp.LpBinary)
            
            prob += pulp.lpSum([(active_df.loc[i, "simulated_ceiling"] - penalty_tracker.get(i, 0)) * vars[i] for i in active_df.index])
            prob += pulp.lpSum([vars[i] for i in active_df.index]) == 11
            prob += pulp.lpSum([active_df.loc[i, "credits"] * vars[i] for i in active_df.index]) <= 100.0
            
            # Role Limits
            prob += pulp.lpSum([vars[i] for i in active_df[active_df["role"] == "WK"].index]) >= min_wk
            prob += pulp.lpSum([vars[i] for i in active_df[active_df["role"] == "WK"].index]) <= max_wk
            prob += pulp.lpSum([vars[i] for i in active_df[active_df["role"] == "BAT"].index]) >= min_bat
            prob += pulp.lpSum([vars[i] for i in active_df[active_df["role"] == "BAT"].index]) <= max_bat
            prob += pulp.lpSum([vars[i] for i in active_df[active_df["role"] == "AR"].index]) >= min_ar
            prob += pulp.lpSum([vars[i] for i in active_df[active_df["role"] == "AR"].index]) <= max_ar
            prob += pulp.lpSum([vars[i] for i in active_df[active_df["role"].isin(["PACE", "SPIN"])].index]) >= min_bowl
            prob += pulp.lpSum([vars[i] for i in active_df[active_df["role"].isin(["PACE", "SPIN"])].index]) <= max_bowl
            
            # Game Theory
            if "Navdeep Saini" in active_df["name"].values and "Arpit Rana" in active_df["name"].values:
                idx_bowler = active_df.index[active_df["name"] == "Navdeep Saini"].tolist()[0]
                idx_batter = active_df.index[active_df["name"] == "Arpit Rana"].tolist()[0]
                prob += vars[idx_bowler] + vars[idx_batter] <= 1
                
            if "Priyansh Arya" in active_df["name"].values and "Yajas Sharma" in active_df["name"].values:
                idx_op1 = active_df.index[active_df["name"] == "Priyansh Arya"].tolist()[0]
                idx_op2 = active_df.index[active_df["name"] == "Yajas Sharma"].tolist()[0]
                prob += vars[idx_op1] - vars[idx_op2] <= 0
                
            for i in active_df.index:
                if active_df.loc[i, "name"] in locked_list:
                    prob += vars[i] == 1
                    
            prob.solve(pulp.PULP_CBC_CMD(msg=False))
            
            if pulp.LpStatus[prob.status] == "Optimal":
                indices = [i for i in active_df.index if vars[i].varValue == 1]
                for idx in indices: penalty_tracker[idx] += 4.5
                
                team_squad = active_df.loc[indices].sort_values(by="simulated_ceiling", ascending=False)
                portfolios.append({
                    "Portfolio ID": f"Team {t+1}",
                    "Captain (2x)": team_squad.iloc[0]["name"],
                    "Vice-Captain (1.5x)": team_squad.iloc[1]["name"],
                    "Total Credits": round(team_squad["credits"].sum(), 1),
                    "Projected Ceiling Total": round(team_squad["simulated_ceiling"].sum(), 1),
                    "Squad Lineup": ", ".join(team_squad["name"].tolist())
                })
                
        res_df = pd.DataFrame(portfolios)
        st.success(f"Generated {len(res_df)} Market-Weighted Portfolios.")
        
        # Portfolio Display
        for idx, row in res_df.iterrows():
            with st.expander(f"🔹 {row['Portfolio ID']} | C: {row['Captain (2x)']} | Pts: {row['Projected Ceiling Total']}"):
                st.markdown(f"**Complete Lineup:** `{row['Squad Lineup']}`")
