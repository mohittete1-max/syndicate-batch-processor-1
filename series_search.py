import requests

# ==============================================================================
# TARGETED SERIES MATCH EXTRACTOR
# ==============================================================================
API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
SERIES_URL = "https://api.cricapi.com/v1/series"
INFO_URL = "https://api.cricapi.com/v1/series_info"

# Keywords for your specific DFS slates
TARGET_KEYWORDS = ["Asia Cup", "Zimbabwe", "South Africa", "European", "ETPL"]

def hunt_for_series_matches():
    print("\n[SYSTEM] Scanning the global Series Database...")
    
    found_series = []
    
    # Step 1: Page through the series database (offsets 0, 25, 50, 75)
    for offset in [0, 25, 50, 75]:
        params = {"apikey": API_KEY, "offset": offset}
        try:
            res = requests.get(SERIES_URL, params=params, timeout=10)
            data = res.json()
            
            if data.get("status") != "success":
                continue
                
            for series in data.get("data", []):
                series_name = series.get("name", "").lower()
                
                # Filter for your specific syndicate targets
                if any(kw.lower() in series_name for kw in TARGET_KEYWORDS):
                    # Prevent duplicates
                    if series.get("id") not in [s['id'] for s in found_series]:
                        found_series.append({
                            "id": series.get("id"),
                            "name": series.get("name")
                        })
        except Exception as e:
            print(f"  [ERROR] Network error at offset {offset}: {e}")
            break
            
    if not found_series:
        print("\n[INFO] Could not locate those specific tournaments. Increase the offset loop to search deeper into the archive.")
        return
        
    # Step 2: Fetch the Match Codes inside those specific Series
    for s in found_series:
        print(f"\n=======================================================")
        print(f"--> Found Target Series: {s['name']}")
        print(f"--> Fetching Match Codes...")
        
        info_params = {"apikey": API_KEY, "id": s["id"]}
        try:
            info_res = requests.get(INFO_URL, params=info_params, timeout=10)
            info_data = info_res.json()
            
            # The API nests the matches inside a matchList array
            match_list = info_data.get("data", {}).get("matchList", [])
            
            if not match_list:
                print("  [-] No matches populated inside this series.")
                continue
                
            for match in match_list:
                print(f"  [Match] {match.get('name', 'Unknown')}")
                print(f"  [ID]    {match.get('id', 'Unknown')}\n")
                
        except Exception as e:
            print(f"  [ERROR] Failed to fetch matches for series: {e}")

if __name__ == "__main__":
    hunt_for_series_matches()
