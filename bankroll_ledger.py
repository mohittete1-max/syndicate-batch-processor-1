import pandas as pd
import os
from datetime import datetime

class QuantLedger:
    def __init__(self, db_path="bankroll_history.csv"):
        self.db_path = db_path
        # Initialize the baseline if the ledger doesn't exist
        if not os.path.exists(self.db_path):
            df = pd.DataFrame(columns=[
                "date", "match", "contest_type", "entry_fee", 
                "result", "payout", "net_profit", "rolling_bankroll"
            ])
            # Injecting your starting Phase 1 baseline
            df.loc[0] = [datetime.now().strftime("%Y-%m-%d"), "INITIAL_DEPOSIT", "-", 0.0, "-", 0.0, 0.0, 153.72]
            df.to_csv(self.db_path, index=False)
            print("[SYSTEM] Initialized new quant ledger with base ₹153.72")

    def log_match(self, match, contest_type, entry_fee, result_won, payout):
        """Logs a completed contest and mathematically updates the bankroll."""
        df = pd.read_csv(self.db_path)
        current_bankroll = df.iloc[-1]["rolling_bankroll"]
        
        net_profit = payout - entry_fee if result_won else -entry_fee
        new_bankroll = current_bankroll + net_profit
        
        new_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match": match,
            "contest_type": contest_type,
            "entry_fee": entry_fee,
            "result": "WIN" if result_won else "LOSS",
            "payout": payout if result_won else 0.0,
            "net_profit": net_profit,
            "rolling_bankroll": round(new_bankroll, 2)
        }
        
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(self.db_path, index=False)
        
        print(f"\n[LEDGER UPDATED] {match} | {contest_type}")
        print(f"Profit/Loss: ₹{net_profit} | New Bankroll: ₹{round(new_bankroll, 2)}")
        
        # Risk Enforcement Check
        next_safe_limit = round(new_bankroll * 0.10, 2)
        print(f"[RISK CONTROL] Maximum safe allocation for next slate: ₹{next_safe_limit}")

if __name__ == "__main__":
    ledger = QuantLedger()
