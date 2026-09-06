import os
import sys
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.cloud import storage

# ==========================================
# 1. DATA INGESTION & VALIDATION
# ==========================================
PORTFOLIO_FILE = "fully_compounded_gpp_portfolio.csv"
OUTPUT_HTML = "portfolio_report.html"

print("Generating interactive Plotly report...")

if not os.path.exists(PORTFOLIO_FILE):
    print(f"❌ Error: Could not find '{PORTFOLIO_FILE}'. Ensure stage 4 completed successfully.")
    sys.exit(1)

df = pd.read_csv(PORTFOLIO_FILE)

# Vectorized extraction of player exposure across the 20 generated lineups
player_cols = [c for c in df.columns if "Player" in c or "player" in c]
if not player_cols:
    # If lineups are stored row-wise (Lineup_ID, Player, Role, Proj, Salary)
    if "Player" in df.columns:
        exposure_df = (
            df["Player"]
            .value_counts(normalize=True)
            .mul(100)
            .round(2)
            .reset_index()
        )
        exposure_df.columns = ["Player", "Exposure_Pct"]
        lineup_summary = df.groupby("Lineup_ID").agg(
            Total_Proj=("Projection", "sum"),
            Total_Salary=("Salary", "sum")
        ).reset_index()
    else:
        # Fallback to column-based player allocation
        player_cols = [c for c in df.columns if c not in ["Lineup", "Lineup_ID", "Total_Proj", "Total_Salary", "Captain", "Vice_Captain"]]
        all_players = df[player_cols].values.flatten()
        exposure_df = (
            pd.Series(all_players)
            .value_counts(normalize=True)
            .mul(len(player_cols) * 100 / 11)  # Scale relative to 11-player roster
            .round(2)
            .reset_index()
        )
        exposure_df.columns = ["Player", "Exposure_Pct"]
        lineup_summary = df.copy()
else:
    # Wide format: Lineup_ID, Player_1 ... Player_11, Total_Proj, Salary
    all_players = df[player_cols].values.flatten()
    exposure_df = (
        pd.Series(all_players)
        .value_counts()
        .div(len(df))
        .mul(100)
        .round(1)
        .reset_index()
    )
    exposure_df.columns = ["Player", "Exposure_Pct"]
    lineup_summary = df.copy()

# Sort exposures descending
exposure_df = exposure_df.sort_values(by="Exposure_Pct", ascending=True)

# ==========================================
# 2. PLOTLY DASHBOARD CONSTRUCTION
# ==========================================
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Portfolio Player Exposure Distribution (%)",
        "Lineup Projected Score Spread",
        "Captaincy Allocation across 20 Teams",
        "Salary Efficiency vs. Projection"
    ),
    specs=[[{"type": "bar"}, {"type": "box"}],
           [{"type": "pie"}, {"type": "scatter"}]]
)

# Panel 1: Player Exposure Bar Chart
fig.add_trace(
    go.Bar(
        x=exposure_df["Exposure_Pct"],
        y=exposure_df["Player"],
        orientation="h",
        marker=dict(color="#1f77b4"),
        name="Exposure %"
    ),
    row=1, col=1
)

# Panel 2: Projection Spread Boxplot
proj_col = next((c for c in ["Total_Proj", "Proj", "Projection"] if c in lineup_summary.columns), None)
if proj_col:
    fig.add_trace(
        go.Box(
            y=lineup_summary[proj_col],
            name="Projected Total",
            boxpoints="all",
            jitter=0.3,
            pointpos=-1.8,
            marker=dict(color="#2ca02c")
        ),
        row=1, col=2
    )

# Panel 3: Captaincy Share Pie Chart
cap_col = next((c for c in ["Captain", "(C)", "C"] if c in df.columns), None)
if cap_col:
    cap_counts = df[cap_col].value_counts().reset_index()
    cap_counts.columns = ["Captain", "Count"]
    fig.add_trace(
        go.Pie(
            labels=cap_counts["Captain"],
            values=cap_counts["Count"],
            hole=0.4,
            name="Captain Share"
        ),
        row=2, col=1
    )

# Panel 4: Salary vs Projection Scatter
salary_col = next((c for c in ["Salary", "Total_Salary"] if c in lineup_summary.columns), None)
if salary_col and proj_col:
    fig.add_trace(
        go.Scatter(
            x=lineup_summary[salary_col],
            y=lineup_summary[proj_col],
            mode="markers+text",
            marker=dict(size=12, color="#d62728", symbol="diamond"),
            name="Lineup Points"
        ),
        row=2, col=2
    )

# Master Layout Styling
fig.update_layout(
    title_text="DFS Syndicate // Quantitative Portfolio Risk & Allocation Dashboard",
    title_x=0.5,
    template="plotly_dark",
    height=850,
    showlegend=False
)

fig.write_html(OUTPUT_HTML)
print(f"Success! Open '{OUTPUT_HTML}' in your browser.")

# ==========================================
# 3. GOOGLE CLOUD STORAGE INTEGRATION
# ==========================================
def upload_to_gcp_bucket(local_file_path, bucket_name):
    """Securely writes local artifacts to a target Google Cloud Storage bucket."""
    try:
        # Authentication is automatically handled via attached GCP Service Account
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(local_file_path)
        blob.upload_from_filename(local_file_path)
        print(f"✅ Success! {local_file_path} securely uploaded to GCP Bucket: {bucket_name}")
    except Exception as exc:
        print(f"❌ Failed to upload {local_file_path} to GCP: {exc}")

target_bucket = os.environ.get("GCP_DFS_BUCKET")

if target_bucket:
    print("\n☁️ Cloud environment detected. Initiating GCP Storage upload...")
    upload_to_gcp_bucket(PORTFOLIO_FILE, target_bucket)
    upload_to_gcp_bucket(OUTPUT_HTML, target_bucket)
else:
    print("\n🖥️ Local run detected (No GCP_DFS_BUCKET variable set). Skipping cloud upload.")
