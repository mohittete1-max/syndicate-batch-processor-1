def fetch_live_pool(match_id):
    """Fetches live player data from CricData with error handling."""
    if CRICDATA_API_KEY == "MISSING_KEY":
        raise ValueError("API Key not found. Ensure config.py is in the same folder.")
        
    url = f"https://api.cricdata.com/v1/matches/{match_id}/fantasy-roster"
    headers = {"Authorization": f"Bearer {CRICDATA_API_KEY}"}
    response = requests.get(url, headers=headers)
    
    try:
        # Attempt to parse the JSON
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        # If it fails, print the raw response to see what went wrong
        print(f"API Error! Status Code: {response.status_code}")
        print(f"Raw Response: {response.text[:250]}")
        raise SystemExit("Exiting: CricData API did not return valid JSON.")
        
    if response.status_code == 200:
        return pd.DataFrame(data.get('players', []))
    else:
        raise ConnectionError(f"API Fetch Failed: {response.status_code} - {data}")
