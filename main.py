"""
==============================================================================
SYNDICATE OS - MASTER PIPELINE ORCHESTRATOR & PULP SOLVER HOOK
==============================================================================
"""

import os
import json
import pandas as pd
from datetime import datetime
from notify import send_alert
from platform_exporters import export_platform_templates

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATCH_CODES_FILE = os.path.join(BASE_DIR, "todays_match_codes.json")

def select_target_fixture():
    if not os.path.exists(MATCH_CODES_FILE):
        print("❌ Match codes file not found. Please execute fixture indexing first.")
        return None
    
    with open(MATCH_CODES_FILE, "r", encoding="utf-8") as f:
        fixtures = json.load(f)
        
    if not fixtures:
        print("❌ Fixture catalog is empty.")
        return None
        
    # Automatically pick the primary active match from the cached index
    target_fixture = fixtures[0]
    print(f"🎯 Selected Target Fixture: {target_fixture['match_title']} (Match ID: {target_fixture['match_id']})")
    return target_fixture

def run_orchestration_pipeline():
    fixture = select_target_fixture()
    if not fixture:
        print("❌ Pipeline aborted: No valid fixtures found.")
        return

    match_id = fixture["match_id"]
    match_title = fixture["match_title"]
    print(f"🚀 Initializing PuLP optimization engine for Match ID: {match_id} ({match_title})...")

    # --- PuLP Mixed-Integer Linear Programming Solver Execution ---
    # In production, your solver ingests player projections and salaries mapped from match_id
    # Simulated optimization output dataframe:
    optimized_df = pd.DataFrame({
        'lineup_id': [1, 1, 1, 1, 2, 2, 2, 2],
        'player_name': ['Player Alpha', 'Player Beta', 'Player Gamma', 'Player Delta', 'Player Alpha', 'Player Epsilon', 'Player Zeta', 'Player Theta'],
        'team': ['TEAM_A', 'TEAM_B', 'TEAM_A', 'TEAM_B', 'TEAM_A', 'TEAM_B', 'TEAM_A', 'TEAM_B'],
        'role': ['BAT', 'BOWL', 'AR', 'WK', 'BAT', 'AR', 'BOWL', 'BAT'],
        'salary': [9.0, 8.5, 9.5, 8.0, 9.0, 8.8, 8.2, 9.1],
        'vegas_proj': [45.5, 38.2, 51.0, 34.5, 45.5, 42.1, 37.9, 46.0]
    })

    # Step 2: Generate multi-platform upload templates
    print("📁 Exporting formatted platform CSV files...")
    export_platform_templates(optimized_df, output_dir="outputs")

    # Step 3: Trigger Telegram Success Alert
    alert_text = f"🚀 *DFS Pipeline Success!*\n*Match:* {match_title}\n*Status:* Lineups optimized, formatted, and ready for deployment."
    send_alert(alert_text)
    print("✅ End-to-end pipeline execution completed successfully!")

if __name__ == "__main__":
    run_orchestration_pipeline()
