# ==========================================
# DYNAMIC BIG BALLS SPORTS DATA FETCHER
# ==========================================
def fetch_dynamic_match_pool(match_id):
    """
    Fetches live match squads and recent performance points dynamically 
    from the Big Balls Sports Data REST API using the unified schema.
    """
    BBS_API_KEY = "bbs_live_000002X0Wnl6gk0edKBnBL5SDCxIwofJqUb67JG9ZRLJrfla"
    
    # Targeting the unified match lineups endpoint
    url = f"https://api.bigballsdata.com/v1/matches/{match_id}/lineups"
    
    headers = {
        "Authorization": f"Bearer {BBS_API_KEY}",
        "Accept": "application/json"
    }
    
    pool = []
    print(f"🔄 Requesting data from Big Balls Sports API for match ID: {match_id}...", flush=True)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"[-] API Error Status Code {response.status_code}. Falling back.", flush=True)
            return []
            
        payload = response.json()
        data = payload.get("data", [])
        
        # Parse the unified Big Balls schema 
        for team_obj in data:
            team_name = team_obj.get("team_name", "Unknown")
            players = team_obj.get("players", [])
            
            for player in players:
                name = player.get("name", "Unknown Player")
                position = player.get("position", "BAT").upper()
                
                # Standardize positions to pipeline roles (WK, BAT, AR, BOWL)
                if "WICKET" in position or "WK" in position:
                    role = "WK"
                elif "ALL" in position or "AR" in position or "MID" in position:
                    role = "AR"
                elif "BOWL" in position or "DEF" in position:
                    role = "BOWL"
                else:
                    role = "BAT"
                    
                recent_points = float(player.get("fantasy_points", 100.0) or 100.0)
                credits_val = float(player.get("credit_value", 8.0) or 8.0)
                
                pool.append({
                    "name": name,
                    "role": role,
                    "team": team_name,
                    "credits": credits_val,
                    "points": recent_points 
                })
        
        print(f"🌐 Successfully fetched {len(pool)} player records from Big Balls Data.", flush=True)
        return pool
        
    except Exception as e:
        print(f"[-] Exception during Big Balls API fetch: {e}", flush=True)
        return []
