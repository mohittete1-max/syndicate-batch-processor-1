import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Solved Lineup Data
players = [
    "G Maxwell (BWV)",
    "H Tector (DNG)",
    "R Ashwin (DNG)",
    "M Adair (BWV)",
    "C Jordan (BWV)",
    "D Mitchell (DNG)",
    "J Little (DNG)",
    "V Shankar (DNG)",
    "D Conway (BWV)",
    "L Tucker (BWV)",
    "P Stirling (BWV)",
]
roles = ["AR", "AR", "BOWL", "AR", "BOWL", "AR", "BOWL", "AR", "BAT", "WK", "BAT"]
credits_spent = [9.0, 8.0, 9.0, 8.5, 8.5, 8.5, 8.5, 7.5, 8.5, 8.0, 8.0]
base_ev = [82.0, 76.0, 66.0, 54.0, 52.0, 50.0, 50.0, 48.0, 48.0, 44.0, 42.0]

# H2H Multipliers: Maxwell (2.0x C), Tector (1.5x VC)
h2h_ev = [
    82.0 * 2.0,
    76.0 * 1.5,
    66.0,
    54.0,
    52.0,
    50.0,
    50.0,
    48.0,
    48.0,
    44.0,
    42.0,
]

# GPP Multipliers: Jordan (2.0x C), Conway (1.5x VC)
gpp_ev = [
    82.0,
    76.0,
    66.0,
    54.0,
    52.0 * 2.0,
    50.0,
    50.0,
    48.0,
    48.0 * 1.5,
    44.0,
    42.0,
]

# Create 2x2 Interactive Subplot Dashboard
fig = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=(
        "Player Base EV vs. Projected Multiplier Ceiling",
        "Roster Team Split (BWV vs DNG)",
        "Credit Allocation by Role",
        "H2H vs GPP Multiplied EV Breakdown",
    ),
    specs=[
        [{"type": "bar"}, {"type": "pie"}],
        [{"type": "bar"}, {"type": "bar"}],
    ],
    vertical_spacing=0.15,
    horizontal_spacing=0.12,
)

# 1. Base EV vs H2H Multiplier
fig.add_trace(
    go.Bar(
        x=players,
        y=base_ev,
        name="Base EV",
        marker_color="#3366CC",
        text=base_ev,
        textposition="auto",
    ),
    row=1,
    col=1,
)
fig.add_trace(
    go.Bar(
        x=players,
        y=h2h_ev,
        name="H2H Multiplied EV (Max C / Tec VC)",
        marker_color="#00CC96",
        text=h2h_ev,
        textposition="auto",
    ),
    row=1,
    col=1,
)

# 2. Team Split Pie Chart
fig.add_trace(
    go.Pie(
        labels=["Belfast Wolves (BWV)", "Dublin Guardians (DNG)"],
        values=[6, 5],
        hole=0.45,
        marker_colors=["#00CC96", "#FF5733"],
    ),
    row=1,
    col=2,
)

# 3. Credit Allocation by Role
fig.add_trace(
    go.Bar(
        x=["All-Rounders (5)", "Bowlers (3)", "Batters (2)", "Wicket-Keeper (1)"],
        y=[41.5, 26.0, 16.5, 8.0],
        name="Credits (Cr)",
        marker_color="#AB63FA",
        text=[41.5, 26.0, 16.5, 8.0],
        textposition="auto",
    ),
    row=2,
    col=1,
)

# 4. H2H vs GPP Comparison
fig.add_trace(
    go.Bar(
        x=["Team 1: H2H Anchor", "Team 2: GPP Leverage"],
        y=[sum(h2h_ev), sum(gpp_ev)],
        name="Total Projected EV",
        marker_color=["#00CC96", "#EF553B"],
        text=[f"{sum(h2h_ev):.1f} EV", f"{sum(gpp_ev):.1f} EV"],
        textposition="auto",
    ),
    row=2,
    col=2,
)

# Layout Configuration
fig.update_layout(
    title_text="<b>Universal Syndicate Protocol: Pre-Lock Lineup Optimization & EV Matrix</b>",
    title_x=0.5,
    template="plotly_dark",
    height=800,
    showlegend=True,
    font=dict(family="Arial, sans-serif", size=12),
)

# Render and Export
fig.write_html("pre_match_lineup_dashboard.html")
fig.show()
