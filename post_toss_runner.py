import requests
import sqlite3

# Credentials and Configuration
API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
DB_PATH = r"C:\Users\User\OneDrive\Desktop\Cricket\cricket_analytics.db"

def fetch_match_squad_and_toss(match_id):
    """Fetches live match info, playing XI, and toss results post-toss."""
    url = f"https://api.cricapi.com/v1/match_info?apikey={API_KEY}&id={match_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"API Error: {response.status_code}")
            return None
            
        payload = response.json()
        if payload.get("status") != "success":
            print("Failed to retrieve match info.")
            return None
            
        data = payload.get("data", {})
        match_name = data.get("name")
        toss_winner = data.get("tossWinner")
        toss_choice = data.get("tossChoice")
        status = data.get("status")
        team_info = data.get("teamInfo", [])
        squads = data.get("squad", [])
        
        print(f"\n=======================================================")
        print(f"🏏 POST-TOSS DATA: {match_name}")
        print(f"=======================================================")
        print(f"📢 Toss: {toss_winner} won the toss and elected to {toss_choice}")
        print(f"📊 Status: {status}")
        
        return {
            "match_id": match_id,
            "name": match_name,
            "toss_winner": toss_winner,
            "toss_choice": toss_choice,
            "squads": squads
        }
        
    except Exception as e:
        print(f"Error fetching post-toss data: {e}")
        return None

def log_post_toss_to_db(match_data):
    """Logs the locked post-toss parameters into SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_toss_logs (
            match_id TEXT PRIMARY KEY,
            name TEXT,
            toss_winner TEXT,
            toss_choice TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        INSERT OR REPLACE INTO post_toss_logs (match_id, name, toss_winner, toss_choice)
        VALUES (?, ?, ?, ?)
    """, (match_data["match_id"], match_data["name"], match_data["toss_winner"], match_data["toss_choice"]))
    
    conn.commit()
    conn.close()
    print("💾 Post-toss state successfully committed to SQLite persistence layer.")

if __name__ == "__main__":
    # Target the England vs Pakistan 3rd Test ID or any active match ID from your DB
    target_match_id = "4d504550-036d-42bd-9f49-4fd0c038be54" 
    
    print(f"Querying post-toss data for match ID: {target_match_id}...")
    match_result = fetch_match_squad_and_toss(target_match_id)
    
    if match_result:
        log_post_toss_to_db(match_result)
