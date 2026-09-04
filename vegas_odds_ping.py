import requests
import json

def ping_the_odds_api():
    # Your active API key is hardcoded here for the test
    api_key = "cbc44005b52548136bcc348e665e2680"
    
    # 1. Fetch all active sports to find valid cricket keys
    print("▶ Pinging The Odds API for active cricket tournaments...")
    sports_endpoint = f"https://api.the-odds-api.com/v4/sports?apiKey={api_key}"
    
    try:
        response = requests.get(sports_endpoint)
        response.raise_for_status()
        sports = response.json()
        
        # Filter for cricket
        cricket_leagues = [s for s in sports if 'cricket' in s['key'].lower()]
        
        if not cricket_leagues:
            print("No active cricket tournaments found at this exact moment.")
            return

        print(f"✅ Found {len(cricket_leagues)} active cricket leagues.")
        
        # 2. Grab the first active cricket league to test the odds endpoint
        target_sport = cricket_leagues[0]['key']
        print(f"▶ Fetching live odds for: {cricket_leagues[0]['title']} ({target_sport})...")
        
        odds_endpoint = f"https://api.the-odds-api.com/v4/sports/{target_sport}/odds"
        params = {
            "api_key": api_key,
            "regions": "uk,eu",
            "markets": "h2h,totals",
            "oddsFormat": "decimal"
        }
        
        odds_response = requests.get(odds_endpoint, params=params)
        odds_response.raise_for_status()
        odds_data = odds_response.json()
        
        if not odds_data:
            print(f"No active odds found for {cricket_leagues[0]['title']}.")
            return
            
        print("\n--- VEGAS SCRIPT CONNECTION TEST SUCCESSFUL ---")
        print("Raw JSON output for the first available match:")
        print(json.dumps(odds_data[0], indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"API Connection Error: {e}")

if __name__ == "__main__":
    ping_the_odds_api()
