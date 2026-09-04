import requests
import json

print("Fetching REAL live and recent matches from Free Cricbuzz...\n")

# Notice the URL is now pointing to /cricket-matches-recent instead of /cricket-match-info
url = "https://free-cricbuzz-cricket-api.p.rapidapi.com/cricket-matches-recent"

headers = {
    "x-rapidapi-host": "free-cricbuzz-cricket-api.p.rapidapi.com",
    "x-rapidapi-key": "b84c777f82mshf8a62983fcca58dp1a6214jsn0eb579d1ea5d"
}

try:
    response = requests.get(url, headers=headers)
    data = response.json()
    
    print("==========================================")
    print("         LIVE & RECENT MATCH DATA         ")
    print("==========================================")
    
    # We will print out the formatted JSON so we can map the exact keys
    if "response" in data and isinstance(data["response"], list):
        print(json.dumps(data["response"][:2], indent=4))
    else:
        # Fallback if the structure is nested differently
        print(json.dumps(data, indent=4)[:1500])
        
    print("\n==========================================\n")
    
except Exception as e:
    print(f"[!] Request Error: {e}")
