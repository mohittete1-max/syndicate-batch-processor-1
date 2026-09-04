import os
import time
import requests
import sqlite3

# ==========================================
# SYSTEM CONFIGURATION
# ==========================================
WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket\Syndicate_Batch_Processor"
os.makedirs(WORKSPACE_DIR, exist_ok=True)

API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
DB_PATH = os.path.join(WORKSPACE_DIR, "cricket_analytics.db")

def fetch_match_squad_and_toss(match_id):
    """Fetches live match info, playing XI, and toss results post-toss."""
    url = f"https://api.cricapi.com/v1/match_info?apikey={API_KEY}&id={match_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"[-] API Error: Status Code {response.status_code}")
            return None
            
        payload = response.json()
        if payload.get("status") != "success":
            print("[-] Failed to retrieve match info from API.")
            return None
            
        data = payload.get("data", {})
        match_name = data.get("name", "Unknown Match")
        toss_winner = data.get("tossWinner")
        toss_choice = data.get("tossChoice")
        status = data.get("status", "Unknown")
        squads = data.get("squad", [])
        
        print(f"\n=======================================================")
        print(f"🏏 LIVE MONITOR: {match_name}")
        print(f"=======================================================")
        print(f"📊 Match Status: {status}")
        
        if not toss_winner or not toss_choice:
            print("⏳ Toss has NOT happened yet. Holding state...")
            return None
            
        print(f"📢 Toss Locked: {toss_winner} won the toss and elected to {toss_choice}")
        print(f"👥 Squad Data Points Found: {len(squads)}")
        
        return {
            "match_id": match_id,
            "name": match_name,
            "toss_winner": toss_winner,
            "toss_choice": toss_choice,
            "squads": squads
        }
        
    except Exception as e:
        print(f"[-] Error fetching post-toss data: {e}")
        return None

def log_post_toss_to_db(match_data):
    """Logs the locked post-toss parameters into SQLite persistence layer."""
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
    target_match_id = "4d504550-036d-42bd-9f49-4fd0c038be54" 
    poll_interval_seconds = 300  # Poll every 5 minutes
    
    print(f"🔄 Automated Toss Monitor initiated for Match ID: {target_match_id}")
    print(f"⏱️ Polling interval set to {poll_interval_seconds} seconds. Press Ctrl+C to stop.")
    
    try:
        while True:
            match_result = fetch_match_squad_and_toss(target_match_id)
            
            if match_result:
                log_post_toss_to_db(match_result)
                print("🎯 Toss successfully captured and logged. Shutting down monitor loop.")
                break
            else:
                print(f"💤 Sleeping for {poll_interval_seconds // 60} minutes before next poll...\n")
                time.sleep(poll_interval_seconds)
                
    except KeyboardInterrupt:
        print("\n🛑 Toss monitor manually stopped by user.")
