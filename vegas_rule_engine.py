import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class VegasBankrollEngine:
    """Implements the Vegas 80/20 Bankroll Management Rule & DFS Risk Engine."""

    def __init__(self, total_bankroll: float, stake_pct: float = 0.20):
        self.total_bankroll = total_bankroll
        self.stake_pct = stake_pct
        self.active_stake = round(self.total_bankroll * self.stake_pct, 2)
        self.vault_balance = round(self.total_bankroll - self.active_stake, 2)

        # 80/20 Contest Allocation
        self.h2h_allocation = round(self.active_stake * 0.80, 2)
        self.gpp_allocation = round(self.active_stake * 0.20, 2)

    def get_summary(self) -> dict:
        return {
            "Total Bankroll": self.total_bankroll,
            "Active Stake": self.active_stake,
            "Protected Vault": self.vault_balance,
            "H2H Allocation (80%)": self.h2h_allocation,
            "GPP Allocation (20%)": self.gpp_allocation,
        }

    def simulate_trajectories(self, num_slates: int = 20, num_sims: int = 100):
        """Simulates bankroll compounding over future slates.

        - Vegas Rule: 65% H2H win-rate (1.8x payout) + 15% GPP cash rate (3.0x
        avg return).
        - Degenerate Strategy: 100% Bankroll in GPPs (20% cash rate, high
        variance).
        """
        np.random.seed(42)

        vegas_paths = np.zeros((num_sims, num_slates + 1))
        degen_paths = np.zeros((num_sims, num_slates + 1))

        vegas_paths[:, 0] = self.total_bankroll
        degen_paths[:, 0] = self.total_bankroll

        for s in range(1, num_slates + 1):
            for i in range(num_sims):
                # --- Vegas Rule Simulation ---
                curr_v_bankroll = vegas_paths[i, s - 1]
                if curr_v_bankroll > 5.0:
                    stake = curr_v_bankroll * self.stake_pct
                    h2h_bet = stake * 0.80
                    gpp_bet = stake * 0.20

                    # H2H outcome (65% win probability)
                    h2h_win = np.random.rand() < 0.65
                    h2h_return = (h2h_bet * 1.80) if h2h_win else 0.0

                    # GPP outcome (15% in-the-money probability)
                    gpp_win = np.random.rand() < 0.15
                    gpp_return = (
                        (gpp_bet * np.random.uniform(2.5, 6.0))
                        if gpp_win
                        else 0.0
                    )

                    new_v_bankroll = (
                        curr_v_bankroll - stake + h2h_return + gpp_return
                    )
                else:
                    new_v_bankroll = curr_v_bankroll
                vegas_paths[i, s] = max(round(new_v_bankroll, 2), 0.0)

                # --- 100% GPP Strategy (No Risk Defense) ---
                curr_d_bankroll = degen_paths[i, s - 1]
                if curr_d_bankroll > 5.0:
                    d_stake = curr_d_bankroll * 0.50  # Over-leveraged sizing
                    d_win = np.random.rand() < 0.22
                    d_return = (
                        (d_stake * np.random.uniform(2.0, 5.0))
                        if d_win
                        else 0.0
                    )
                    new_d_bankroll = curr_d_bankroll - d_stake + d_return
                else:
                    new_d_bankroll = curr_d_bankroll
                degen_paths[i, s] = max(round(new_d_bankroll, 2), 0.0)

        return vegas_paths, degen_paths


def build_vegas_plotly_dashboard(
    engine: VegasBankrollEngine,
    output_html: str = "vegas_rule_dashboard.html",
):
    """Generates an interactive Plotly dashboard for portfolio distribution and growth."""
    summary = engine.get_summary()
    vegas_paths, degen_paths = engine.simulate_trajectories(
        num_slates=25, num_sims=50
    )
    slates = list(range(26))

    # Calculate median trajectories
    vegas_median = np.median(vegas_paths, axis=0)
    degen_median = np.median(degen_paths, axis=0)

    # Subplots setup
    fig = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.4, 0.6],
        specs=[[{"type": "domain"}, {"type": "xy"}]],
        subplot_titles=(
            "<b>Slate Capital Deployment</b>",
            "<b>25-Slate Compounding Trajectory (Median EV)</b>",
        ),
    )

    # 1. Donut Chart - Capital Allocation
    labels = ["Protected Vault", "H2H Anchor (80%)", "GPP Upside (20%)"]
    values = [
        summary["Protected Vault"],
        summary["H2H Allocation (80%)"],
        summary["GPP Allocation (20%)"],
    ]
    colors = ["#2b3a4a", "#00c853", "#ffd600"]

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#111", width=2)),
            textinfo="label+value+percent",
            texttemplate="%{label}<br>₹%{value:.2f}<br>(%{percent})",
            hoverinfo="label+value",
        ),
        row=1,
        col=1,
    )

    # 2. Line Chart - Compounding Curve Comparison
    fig.add_trace(
        go.Scatter(
            x=slates,
            y=vegas_median,
            mode="lines+markers",
            name="Vegas 80/20 Rule (Disciplined)",
            line=dict(color="#00e676", width=3),
            marker=dict(size=6),
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Scatter(
            x=slates,
            y=degen_median,
            mode="lines+markers",
            name="Unhedged GPP Chasing (High Ruin Risk)",
            line=dict(color="#ff1744", width=2, dash="dot"),
            marker=dict(size=5),
        ),
        row=1,
        col=2,
    )

    # Layout styling
    fig.update_layout(
        template="plotly_dark",
        title_text=f"<b>Universal Syndicate Protocol: Vegas Rule Engine (Current Bankroll: ₹{engine.total_bankroll:.2f})</b>",
        title_font_size=18,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5
        ),
        margin=dict(l=40, r=40, t=80, b=80),
        height=550,
    )

    fig.update_xaxes(title_text="Slates Played", row=1, col=2, gridcolor="#333")
    fig.update_yaxes(
        title_text="Bankroll (₹)", row=1, col=2, gridcolor="#333"
    )

    fig.write_html(output_html)
    print(f"✅ Dashboard generated successfully: {output_html}")
    fig.show()


if __name__ == "__main__":
    # Initialize with current bankroll and 20% micro-stake limit
    current_bankroll = 115.72
    engine = VegasBankrollEngine(
        total_bankroll=current_bankroll, stake_pct=0.20
    )

    # Print summary to console
    print("\n" + "=" * 55)
    print("      VEGAS 80/20 RULE - SLATE ALLOCATION MATRIX")
    print("=" * 55)
    for k, v in engine.get_summary().items():
        print(f"  ▶ {k:<25}: ₹{v:.2f}")
    print("=" * 55 + "\n")

    # Render interactive Plotly chart
    build_vegas_plotly_dashboard(engine)
