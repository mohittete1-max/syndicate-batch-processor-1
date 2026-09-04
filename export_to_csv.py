import pandas as pd
import os
from datetime import datetime
import uuid

def log_match_to_ledger(tournament_name, match_name, teams_generated, total_investment):
    """Logs financial data and the specific global tournament into the Power BI vault."""
    csv_file = "PowerBI_Syndicate_Ledger.csv"
    
    # Create the new row of data for the current match
    new_data = pd.DataFrame([{
        "Ledger_ID": str(uuid.uuid4())[:8],
        "Tournament_Name": tournament_name,  # <--- Now 100% dynamic
        "Match_Name": match_name,
        "Teams_Generated": teams_generated,
        "Total_Investment_INR": total_investment,
        "Total_Return_INR": 0.0, 
        "Execution_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

    # Append to the existing ledger
    if os.path.exists(csv_file):
        new_data.to_csv(csv_file, mode='a', header=False, index=False)
        print(f"Successfully appended {match_name} ({tournament_name}) to the ledger.")
    else:
        new_data.to_csv(csv_file, mode='w', header=True, index=False)
        print("Created new syndicate ledger and logged first match.")
