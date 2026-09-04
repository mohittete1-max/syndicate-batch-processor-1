import requests

API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
MATCH_ID = "ac956620-023b-4430-8f78-1877951a44d7"

def scout_match_keys():
    print(f"Inspecting keys for Match ID: {MATCH_ID}...\n")
    url = f"https://api.cricapi.com/v1/match_info?apikey={API_KEY}&id={MATCH_ID}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        response_block = data.get("data", {})
        
        print("==========================================")
        print("      CRICAPI DATA STRUCTURE KEYS         ")
        print("==========================================")
        print(f"Top-level keys available: {list(response_block.keys())}")
        
        if "teamInfo" in response_block:
            print("\n--- Team Info Found ---")
            for team in response_block["teamInfo"]:
                print(f"Team: {team.get('name')} ({team.get('shortname')})")
                
        if "scorecard" in response_block:
            print("\n--- Scorecard Structure Found ---")
            print("Scorecard keys / teams present.")
            
        if "matchStarted" in response_block:
            print(f"\nMatch Started: {response_block.get('matchStarted')}")
            print(f"Match Ended: {response_block.get('matchEnded')}")
            
        print("==========================================\n")
        
    except Exception as e:
        print(f"[!] Request Error: {e}")

if __name__ == "__main__":
    scout_match_keys()
