import os
import requests
import pandas as pd

# ==============================================================================
# LIVE BATCH EXTRACTOR (CRICDATA FANTASY SQUAD)
# ==============================================================================
API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
BASE_URL = "https://api.cricapi.com/v1/match_squad"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Live Match IDs verified on the CricData network
TARGET_FIXTURES = {
    "TAN_W_vs_UGA_W": "1fa3bd8a-4bac-4ebb-b022-aba8281467e3", 
    "CHN_W_vs_OMN_W": "2f7b4b4d-222e-4a4b-93f8-5794ed89ad24",
    "ENG_vs_PAK": "cc1c57c0-7ecf-4556-8465-47bbac896427"
}

def batch_extract_squads():
    print("\n[SYSTEM] Initiating Live Batch Extraction with CricData Token...")
    
    for match_tag, match_id in TARGET_FIXTURES.items():
        # The Fantasy Squad endpoint uses 'id', not 'offset'
        params = {"apikey": API_KEY, "id": match_id}
        print(f"\n  --> Extracting {match_tag} (ID: {match_id})...")
        
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") != "success" or "data" not in data:
                print(f"  [WARN] Failed to fetch {match_tag}. Reason: {data.get('reason', 'Unknown API Error')}")
                continue
                
            rows = []
            for team_info in data["data"]:
                team_short = "".join([w[0] for w in team_info.get("teamName", "UNK").split()]).upper()[:3]
                for player in team_info.get("players", []):
                    
                    # Smart Role Mapping
                    p_role_raw = str(player.get("role", "AR")).lower()
                    if "wicketkeeper" in p_role_raw or "wk" in p_role_raw: p_role = "WK"
                    elif "bat" in p_role_raw: p_role = "BAT"
                    elif "bowl" in p_role_raw: p_role = "BOWL"
                    else: p_role = "AR"
                    
                    # Structuring exactly how the Syndicate OS needs it
                    rows.append({
                        "player_name": player.get("name"), 
                        "team": team_short, 
                        "role": p_role,
                        "credits": 8.5,             
                        "projected_points": 45.0,   
                        "ownership": 15.0,          
                        "is_playing": 1
                    })
                    
            df = pd.DataFrame(rows)
            output_file = os.path.join(BASE_DIR, f"{match_tag}.csv")
            df.to_csv(output_file, index=False)
            print(f"  [SUCCESS] Saved {len(df)} live players to {match_tag}.csv")
            
        except Exception as e:
            print(f"  [ERROR] Extraction failed for {match_tag}: {e}")

if __name__ == "__main__":
    batch_extract_squads()
