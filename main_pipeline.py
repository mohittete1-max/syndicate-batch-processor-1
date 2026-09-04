import os
import sys
import time
import subprocess

# Force all Python child scripts to use UTF-8 to prevent Windows emoji crashes
os.environ["PYTHONIOENCODING"] = "utf-8"

def run_script(script_name, description):
    """Executes a target Python script and mimics the standard pipeline logs."""
    print(f"> Executing: {description} ({script_name})...")
    print("-" * 65)
    start_time = time.time()
    
    try:
        # Added encoding="utf-8" so Windows safely reads the script outputs
        result = subprocess.run(
            [sys.executable, script_name], 
            capture_output=True, 
            text=True, 
            encoding="utf-8"
        )
        
        if result.stdout:
            print(result.stdout.strip())
        
        if result.returncode == 0:
            elapsed = time.time() - start_time
            print("-" * 65)
            print(f"[OK] {script_name} finished successfully in {elapsed:.2f}s.")
        else:
            if result.stderr:
                print(result.stderr.strip())
            print("-" * 65)
            print(f"[ERROR] {script_name} encountered an error (Code: {result.returncode}).")
            
    except FileNotFoundError:
        print(f"[ERROR] Could not find {script_name} in the current directory.")
        print("-" * 65)

def print_menu():
    print("\n" + "="*65)
    print("       UNIVERSAL SYNDICATE PROTOCOL - MASTER PIPELINE")
    print("                Automated DFS Cricket Engine")
    print("="*65)
    print("1. Full Pre-Match Flow (Fetch Data -> Optimize -> Export Lineups)")
    print("2. Run Lineup Optimizer Only (Fast Solve / Local Data)")
    print("3. Run Post-Match Performance Audit (Generate Report & Dashboard)")
    print("4. Fetch Live API Data Only")
    print("5. Exit")
    print("="*65)

def main():
    while True:
        print_menu()
        choice = input("Enter choice (1-5): ").strip()

        if choice == '1':
            print("\n[PHASE 1] Live Roster & Match Ingestion\n")
            run_script("fetch_cricket_data.py", "Fetching live match fixtures & rosters")
            
            print("\n[PHASE 2] Dual-Lineup Optimization Engine\n")
            run_script("h2h_cash_optimizer.py", "Bankroll Protector (Team_1_H2H_Cash)")
            print("") 
            run_script("grand_league_dual_optimizer.py", "Jackpot Hunter (Team_2_GPP_Jackpot)")
            
            input("\nPress Enter to return to the main menu...")

        elif choice == '2':
            print("\n[PHASE 2] Dual-Lineup Optimization Engine (Local Data)\n")
            run_script("h2h_cash_optimizer.py", "Bankroll Protector (Team_1_H2H_Cash)")
            print("") 
            run_script("grand_league_dual_optimizer.py", "Jackpot Hunter (Team_2_GPP_Jackpot)")
            
            input("\nPress Enter to return to the main menu...")

        elif choice == '3':
            print("\n[PHASE 3] Post-Match Performance Audit\n")
            run_script("generate_report.py", "Compiling variance report & HTML dashboard")
            
            input("\nPress Enter to return to the main menu...")

        elif choice == '4':
            print("\n> Executing: Live API Data Fetcher\n")
            run_script("fetch_cricket_data.py", "Live API Data Fetcher")
            
            input("\nPress Enter to return to the main menu...")

        elif choice == '5':
            print("\nShutting down pipeline. Good luck on the slate!")
            sys.exit(0)
        else:
            print("\n[ERROR] Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
