import requests

API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
SEARCH_TERMS = ["kovai", "tiruppur", "lkk", "itt", "tamizhans"]

def aggressive_match_search():
    print("Initiating aggressive deep-scan across CricAPI (Offsets 0 to 250)...\n")
    
    url_base = "https://api.cricapi.com/v1/matches"
    found = False
    
    for offset in range(0, 251, 25):
        print(f"[*] Scanning offset {offset}...")
        url = f"{url_base}?apikey={API_KEY}&offset={offset}"
        try:
            res = requests.get(url, timeout=10).json()
            if res.get("status") == "success":
                matches = res.get("data", [])
                for m in matches:
                    m_name = m.get("name", "").lower()
                    if any(term in m_name for term in SEARCH_TERMS):
                        print("\n=========================================================")
                        print("                 🚨 MATCH ID LOCATED 🚨                  ")
                        print("=========================================================")
                        print(f"ID: {m.get('id')}")
                        print(f"Match: {m.get('name', 'Unknown')}")
                        print(f"Status: {m.get('status', 'Unknown')}")
                        print(f"Date: {m.get('date', 'Unknown')}")
                        print("=========================================================\n")
                        found = True
                
                if found:
                    return
        except Exception as e:
            print(f"[-] Error at offset {offset}: {e}")
            
    if not found:
        print("\n[-] Scan complete. The match has not been pushed to the active API feed yet.")

if __name__ == "__main__":
    aggressive_match_search()
