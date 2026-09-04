"""
==============================================================================
SYNDICATE OS - RAPIDAPI SCHEDULE FETCHER & MASTER FIXTURE INDEXER
==============================================================================
"""

import os
import json
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATCH_CODES_FILE = os.path.join(BASE_DIR, "todays_match_codes.json")

RAPIDAPI_KEY = "b84c777f82mshf8a62983fcca58dp1a6214jsn0eb579d1ea5d"
RAPIDAPI_HOST = "free-cricbuzz-cricket-api.p.rapidapi.com"
HEADERS = {
    "Content-Type": "application/json",
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": RAPIDAPI_KEY
}

def fetch_endpoint(endpoint):
    url = f"https://{RAPIDAPI_HOST}/{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"  [API ERROR] Endpoint '/{endpoint}' failed: {e}")
    return {}

def parse_and_index_fixtures():
    current_date_str = datetime.now().strftime("%b %d %Y").upper()
    print(f"\n[SYSTEM] Querying multi-endpoint RapidAPI pools. Indexing all matches for selection: {current_date_str}")
    
    payloads = [
        fetch_endpoint("cricket-matches-live"),
        fetch_endpoint("cricket-matches-upcoming"),
        fetch_endpoint("cricket-schedule"),
        fetch_endpoint("cricket-schedule-all")
    ]
    
    if all(not p for p in payloads):
        print("  [ERROR] Empty responses received from ALL endpoints. Check your API key limits or network connection.")
        return

    extracted_fixtures = []
    seen_ids = set()

    def recursive_search(node, inherited_series="General Series"):
        if isinstance(node, dict):
            current_series = (
                node.get("seriesName") or 
                node.get("tourName") or 
                node.get("seriesDesc") or 
                inherited_series
            )
            
            m_id = node.get("matchId") or node.get("id") or node.get("match_id")
            if m_id and str(m_id) not in seen_ids:
                seen_ids.add(str(m_id))
                
                match_info = node.get("matchInfo", node)
                
                t1 = ""
                t2 = ""
                for team_key in ["team1", "homeTeam", "t1"]:
                    if team_key in match_info and isinstance(match_info[team_key], dict):
                        t1 = match_info[team_key].get("teamSName") or match_info[team_key].get("name") or match_info[team_key].get("matchTeamInfo")
                for team_key in ["team2", "awayTeam", "t2"]:
                    if team_key in match_info and isinstance(match_info[team_key], dict):
                        t2 = match_info[team_key].get("teamSName") or match_info[team_key].get("name") or match_info[team_key].get("matchTeamInfo")

                desc = match_info.get("matchDesc") or node.get("matchDesc") or node.get("matchTitle") or node.get("name")
                
                if t1 and t2:
                    match_title = f"{t1} vs {t2} ({desc})" if desc else f"{t1} vs {t2}"
                else:
                    match_title = desc or f"Match_{m_id}"

                date_val = node.get("startDate") or node.get("matchDate") or node.get("date") or match_info.get("startDate") or "TBD"
                
                if str(date_val).isdigit() and len(str(date_val)) >= 10:
                    try:
                        date_val = datetime.fromtimestamp(int(str(date_val)[:10])).strftime("%a, %b %d %Y")
                    except Exception:
                        pass

                safe_filename = "".join([c if c.isalnum() else "_" for c in str(match_title)])[:40] + ".csv"
                extracted_fixtures.append({
                    "match_file": safe_filename,
                    "match_id": str(m_id),
                    "series": str(current_series),
                    "match_title": str(match_title),
                    "date": str(date_val)
                })

            for val in node.values():
                recursive_search(val, inherited_series=current_series)
        elif isinstance(node, list):
            for item in node:
                recursive_search(item, inherited_series=inherited_series)

    for data in payloads:
        if data:
            recursive_search(data)

    if extracted_fixtures:
        with open(MATCH_CODES_FILE, "w", encoding="utf-8") as f:
            json.dump(extracted_fixtures, f, indent=4)
        print(f"[SUCCESS] Saved complete list of {len(extracted_fixtures)} fixtures to '{os.path.basename(MATCH_CODES_FILE)}'.")
        
        print(f"\n--- MASTER FIXTURE CATALOG (READY FOR MANUAL SELECTION) ---")
        print(f"{'DATE':<22} | {'SERIES':<35} | {'MATCH TITLE':<30} | {'MATCH ID'}")
        print("-" * 100)
        
        for fx in extracted_fixtures:
            date_display = fx['date'][:22] if fx['date'] != "TBD" else "Upcoming"
            print(f"{date_display:<22} | {fx['series'][:35]:<35} | {fx['match_title'][:30]:<30} | {fx['match_id']}")
    else:
        print("[INFO] No fixtures found across schedule payload pools.")

if __name__ == "__main__":
    parse_and_index_fixtures()
