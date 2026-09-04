import os
import glob
import shutil
import subprocess
import pandas as pd

def find_true_raw_data(match_target):
    """Scans for the true 22-man raw squad file for a given match."""
    possible_files = glob.glob(f"*{match_target}*.csv")
    
    for file in possible_files:
        # Ignore known outputs or staging files
        if "H2H_Cash" in file or "match_squad_data" in file:
            continue
            
        try:
            df = pd.read_csv(file)
            # A true raw squad will have ~22 players. An old lineup will have 11.
            if len(df) > 15:
                return file
        except:
            pass
    return None

def run_smart_pipeline():
    print("=================================================================")
    print("       UNIVERSAL SYNDICATE PROTOCOL - PHASE 1 BATCH              ")
    print("=================================================================")
    
    # 🎯 TARGET LIST: All 5 daily fixtures loaded
    TARGET_MATCHES = [
        "ADF_vs_ECR",
        "ECR_vs_ADF",
        "SA_vs_NAM",
        "SCO_W_vs_NED_W",
        "THA_W_vs_HK_W"
    ]
    
    print(f"[SYSTEM] Locked onto {len(TARGET_MATCHES)} target fixtures. Operating in H2H ONLY mode.\n")

    for match_name in TARGET_MATCHES:
        print("-" * 65)
        print(f"> INITIATING PHASE 1 PIPELINE FOR: {match_name.replace('_', ' ')}")
        print("-" * 65)
        
        # 1. SMART FILE FINDER
        raw_file = find_true_raw_data(match_name)
        
        if not raw_file:
            print(f"  [ERROR] Could not find a valid 22-man raw squad file for {match_name}.")
            print(f"          Ensure your raw CricData export for this match is in the folder.")
            continue
            
        print(f"  --> Sourcing data from verified raw file: {raw_file}")
        shutil.copy(raw_file, "match_squad_data.csv")
        
        # 2. Context Layer (Pitch/Weather)
        print("  --> Running Environmental Pre-processors...")
        if os.path.exists("meteo.py"):
            subprocess.run(["python", "meteo.py"])
        if os.path.exists("global_pitch.py"):
            subprocess.run(["python", "global_pitch.py"])
            
        # 3. Optimization Layer
        print("  --> Running Ultimate Hybrid H2H Engine (h2h_cash_optimizer.py)...")
        subprocess.run(["python", "h2h_cash_optimizer.py"])
        
        # 4. Save Final Output & Display Roster
        output_file = "Team_1_H2H_Cash.csv"
        final_filename = f"{match_name}_H2H_Cash.csv"
        
        if os.path.exists(output_file):
            shutil.move(output_file, final_filename)
            print(f"  [SAVED] {final_filename}")
            
            try:
                df = pd.read_csv(final_filename)
                print(f"\n  --- {match_name} Final Roster ---")
                print(df[['player_name', 'role', 'credits', 'projected_points', 'Multiplier_Tag']].to_string(index=False))
                print("\n")
            except Exception as e:
                print(f"  [ERROR] Could not display roster for {match_name}: {e}")
                
        else:
            print(f"  [ERROR] Lineup generation failed for {match_name}. Check roster constraints.\n")
            
    # Cleanup Staging Data
    if os.path.exists("match_squad_data.csv"):
        os.remove("match_squad_data.csv")
        
    print("=================================================================")
    print("[BATCH COMPLETE] Phase 1 Cash allocations processed.")
    print("=================================================================")

if __name__ == "__main__":
    run_smart_pipeline()
