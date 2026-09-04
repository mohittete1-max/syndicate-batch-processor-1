import os
import requests
import pandas as pd

API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
BASE_URL = "https://api.cricapi.com/v1"
WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket\Syndicate_Batch_Processor"

def fetch_live_matches():
    """Fetches current active matches using the CricData API."""
    url = f"{BASE_URL}/currentMatches"
    params = {"apikey": API_KEY, "offset": 0}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("status") == "success":
            return data.get("data", [])
        print(f"API Error: {data}")
        return []
    except Exception as e:
        print(f"Request failed: {e}")
        return []

def fetch_match_squad(match_id: str):
    """Fetches official team squads and player roles for a given match ID."""
    url = f"{BASE_URL}/match_squad"
    params = {"apikey": API_KEY, "id": match_id}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("status") == "success":
            return data.get("data", [])
        return []
    except Exception as e:
        print(f"Squad fetch failed for {match_id}: {e}")
        return []

def fetch_fantasy_points(match_id: str):
    """Retrieves player-wise and role-wise fantasy points based on active rulesets."""
    url = f"{BASE_URL}/match_points"
    params = {"apikey": API_KEY, "id": match_id}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("status") == "success":
            return data.get("data", [])
        return []
    except Exception as e:
        print(f"Fantasy points fetch failed for {match_id}: {e}")
        return []

if __name__ == "__main__":
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    matches = fetch_live_matches()
    print(f"Found {len(matches)} active matches.")
    for match in matches[:3]:
        print(f"- Match: {match.get('name')} | ID: {match.get('id')}")
