import requests

def find_asia_cup_match():
    url = "https://api.bigballsdata.com/v1/matches?sport=cricket&limit=200"
    headers = {
        "Authorization": "Bearer bbs_live_000002X0Wnl6gk0edKBnBL5SDCxIwofJqUb67JG9ZRLJrfla",
        "Accept": "application/json"
    }
    
    print("🔍 Searching database for Asia Cup, Hong Kong, or Women's fixtures...", flush=True)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            matches = response.json().get("data", [])
            found = False
            
            for m in matches:
                home = m.get("home", {}).get("name", "")
                away = m.get("away", {}).get("name", "")
                league = m.get("league", "")
                match_id = m.get("id")
                
                text = f"{home} vs {away} | {league}".lower()
                
                if "asia" in text or "cup" in text or "hong" in text or "hk" in text:
                    print(f"🎯 Match: {home} vs {away} | League: {league} | Status: {m.get('status')}")
                    print(f"UUID: {match_id}")
                    print("-" * 70)
                    found = True
                    
            if not found:
                print("[-] No matches matching 'asia', 'cup', or 'hong kong' found.")
        else:
            print(f"[-] API Error: {response.status_code}")
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    find_asia_cup_match()
