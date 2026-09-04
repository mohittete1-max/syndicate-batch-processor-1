import sys
import subprocess

# ==============================================================================
# AUTO-DEPENDENCY CHECK & INSTALL
# ==============================================================================
try:
    from curl_cffi import requests
except ImportError:
    print("[SYSTEM] 'curl_cffi' module not found. Installing modern Cloudflare bypass...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "curl-cffi"])
    from curl_cffi import requests

# ==============================================================================
# ULTIMATE CRICINFO SCHEDULE SCRAPER (TLS IMPERSONATION)
# ==============================================================================
def scrape_cricinfo_schedule():
    print("\n[SYSTEM] Deploying Chrome TLS Impersonation to bypass Cloudflare WAF...")
    
    url = "https://hs-consumer-api.espncricinfo.com/v1/pages/matches/current?lang=en"
    
    try:
        # curl_cffi perfectly mimics Google Chrome's TLS and HTTP/2 network packets
        response = requests.get(url, impersonate="chrome", timeout=15)
        
        if response.status_code != 200:
            print(f"  [ERROR] Bypass failed. HTTP Status: {response.status_code}")
            return
            
        data = response.json()
        matches = data.get("matches", [])
        
        if not matches:
            print("  [WARN] Connected successfully, but no matches returned.")
            return
            
        print("\n[SUCCESS] Cloudflare Firewall Bypassed! Retrieved live matches:\n")
        print(f"{'Series / Tournament':<40} {'Match Name':<45} {'Match ID'}")
        print("-" * 105)
        
        for match in matches:
            series_name = match.get("series", {}).get("name", "Unknown Series")
            
            # Extract team names safely
            teams = match.get("teams", [])
            team1 = teams[0].get("team", {}).get("name", "TBA") if len(teams) > 0 else "TBA"
            team2 = teams[1].get("team", {}).get("name", "TBA") if len(teams) > 1 else "TBA"
                
            match_title = f"{team1} vs {team2}"
            match_id = match.get("objectId", "N/A")
            
            print(f"{series_name[:38]:<40} {match_title[:43]:<45} {match_id}")
            
        print("\n" + "=" * 105)
        print("Copy the Match ID you need for the Syndicate OS pipeline.")
        
    except Exception as e:
        print(f"  [ERROR] Network or parsing error occurred: {e}")

if __name__ == "__main__":
    scrape_cricinfo_schedule()
