import os
import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable, lpSum


def run_apex_dual_optimizer():
  try:
    csv_path = "match_squad_data.csv"
    if not os.path.exists(csv_path):
      raise FileNotFoundError(f"Missing active roster file: {csv_path}")

    df = pd.read_csv(csv_path)

    # Sanitize and ensure mandatory columns exist to prevent crashes
    required_cols = {
        "ceiling_ev": 50.0,
        "differential_bonus": 5.0,
        "ownership": 12.0,
        "credits": 8.5,
        "role": "AR",
    }
    for col, default_val in required_cols.items():
      if col not in df.columns:
        df[col] = default_val

    # Clean any scientific notation or string pollution in numerics
    for col in ["ceiling_ev", "differential_bonus", "ownership", "credits"]:
      df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default_val)

    print(f"Loaded {len(df)} players successfully for optimization.")

    # Optimization Setup
    prob = LpProblem("Apex_GPP_Jackpot_Optimizer", LpMaximize)
    x = {i: LpVariable(f"x_{i}", cat="Binary") for i in df.index}
    c = {i: LpVariable(f"c_{i}", cat="Binary") for i in df.index}
    vc = {i: LpVariable(f"vc_{i}", cat="Binary") for i in df.index}

    prob += lpSum(
        x[i]
        * (
            df.loc[i, "ceiling_ev"]
            + (1.5 * df.loc[i, "differential_bonus"])
            + (2.0 * (df.loc[i, "ownership"] < 15.0))
        )
        + c[i] * (df.loc[i, "ceiling_ev"] * 2.0)
        + vc[i] * (df.loc[i, "ceiling_ev"] * 1.5)
        for i in df.index
    )

    prob += lpSum(x[i] for i in df.index) == 11
    prob += lpSum(c[i] for i in df.index) == 1
    prob += lpSum(vc[i] for i in df.index) == 1

    for i in df.index:
      prob += c[i] <= x[i]
      prob += vc[i] <= x[i]
      prob += c[i] + vc[i] <= 1

    prob += lpSum(x[i] * df.loc[i, "credits"] for i in df.index) <= 100

    prob.solve()

    selected_indices = [i for i in df.index if x[i].value() == 1]
    result_df = df.loc[selected_indices].copy()

    result_df.to_csv("Team_2_GPP_Jackpot.csv", index=False)
    print("✅ Optimization complete. Lineup exported successfully.")
    return result_df

  except Exception as e:
    print(f"❌ Optimizer Error: {e}")
    raise e


if __name__ == "__main__":
  run_apex_dual_optimizer()
