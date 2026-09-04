import sqlite3
import numpy as np
from fastmcp import FastMCP

# Initialize the Server
mcp = FastMCP(name="SyndicateQuantDesk")

# 1. Expose SQLite Persistence as a Resource
@mcp.resource("sqlite://locked_lineups")
def read_locked_lineups() -> str:
    """Reads the locked GPP lineups from the local database."""
    conn = sqlite3.connect(r"C:\Users\User\OneDrive\Desktop\Cricket\cricket_analytics.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locked_lineups ORDER BY timestamp DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return str(rows)

# 2. Expose the Simulator as a Tool
@mcp.tool
def run_monte_carlo(base_projection: float, multiplier: float, noise: float = 0.12) -> float:
    """Runs a stochastic simulation to calculate a player's 90th percentile ceiling."""
    score = base_projection * multiplier
    sims = np.random.normal(loc=score, scale=score * noise, size=50)
    return float(np.percentile(sims, 90))

# 3. Expose the Dispatcher as a Tool
@mcp.tool
def dispatch_telegram_alert(message: str) -> str:
    """Dispatches a custom markdown alert to the trading desk channel."""
    # Insert the standard requests.post logic here
    return "Alert dispatched successfully."

if __name__ == "__main__":
    mcp.run()
