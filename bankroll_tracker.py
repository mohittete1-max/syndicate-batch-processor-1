# bankroll_tracker.py
import pandas as pd
import os

LEDGER_FILE = "bankroll_ledger.csv"

def initialize_ledger():
    """Ensures the tracking ledger exists."""
    if not os.path.exists(LEDGER_FILE):
        df = pd.DataFrame(columns=[
            "Contest_ID", "Match_Name", "Entry_Fee", "Winnings", "Net_Profit", "ROI_%", "Status"
        ])
        df.to_csv(LEDGER_FILE, index=False)

def log_contest(contest_id, match_name, entry_fee, winnings):
    """Logs contest results, computes returns, and updates the local CSV ledger."""
    initialize_ledger()
    df = pd.read_csv(LEDGER_FILE)
    
    net_profit = winnings - entry_fee
    roi = (net_profit / entry_fee) * 100 if entry_fee > 0 else 0.0
    status = "ITM (In The Money)" if winnings > entry_fee else "Loss"
    
    new_record = {
        "Contest_ID": contest_id,
        "Match_Name": match_name,
        "Entry_Fee": entry_fee,
        "Winnings": winnings,
        "Net_Profit": net_profit,
        "ROI_%": round(roi, 2),
        "Status": status
    }
    
    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    df.to_csv(LEDGER_FILE, index=False)
    print(f"Ledger Updated -> {match_name} | Net Profit: {net_profit} | ROI: {roi:.2f}%")

def print_performance_summary():
    """Calculates overall bankroll statistics and cumulative portfolio yield."""
    initialize_ledger()
    df = pd.read_csv(LEDGER_FILE)
    
    if df.empty:
        print("Bankroll Ledger is currently empty. Log your first contest to view metrics.")
        return
        
    total_invested = df["Entry_Fee"].sum()
    total_returned = df["Winnings"].sum()
    total_profit = df["Net_Profit"].sum()
    overall_roi = (total_profit / total_invested) * 100 if total_invested > 0 else 0.0
    win_rate = (len(df[df["Net_Profit"] > 0]) / len(df)) * 100
    
    print("\n==================================================")
    print("      APEX CRICKET ALPHA - PERFORMANCE LEDGER     ")
    print("==================================================")
    print(f"Total Contests Entered: {len(df)}")
    print(f"Total Capital Invested: {total_invested:.2f}")
    print(f"Total Payout Returns:   {total_returned:.2f}")
    print(f"Net Cumulative Profit:  {total_profit:.2f}")
    print(f"Overall Portfolio ROI:  {overall_roi:.2f}%")
    print(f"Contest Win Rate:       {win_rate:.1f}%")
    print("==================================================\n")
    return df

if __name__ == "__main__":
    # Sample test entry pre-configured for immediate execution
    log_contest("HUNDRED_01", "The Hundred Eliminator", 100.0, 320.0)
    print_performance_summary()
