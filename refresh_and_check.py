import requests
import sqlite3
from datetime import datetime, timedelta

API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
DB_PATH = r"C:\Users\User\OneDrive\Desktop\Cricket\cricket_analytics.db"

def refresh_fixtures():
    """Pulls fresh fixtures from CricAPI and updates SQLite."""
    url = f"https://api.cricapi.com/v1/matches?apikey={API_KEY}&offset=0"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print("API fetch failed during refresh.")
            return False
            
        payload = response.json()
        if payload.get("status") != "success":
            return False
            
        matches = payload.get("data", [])
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS upcoming_matches (
                id TEXT PRIMARY KEY,
                name TEXT,
                matchType TEXT,
                date TEXT,
                venue TEXT,
                status TEXT
            )
        """)
        
        for match in matches:
            cursor.execute("""
                INSERT OR REPLACE INTO upcoming_matches (id, name, matchType, date, venue, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (match.get("id"), match.get("name"), match.get("matchType"), 
                  match.get("date"), match.get("venue"), match.get("status")))
                  
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error refreshing database: {e}")
        return False

def get_tomorrow_matches():
    """Queries SQLite for matches scheduled for tomorrow."""
    # Dynamically calculate tomorrow's date format (e.g., Sep 03, 2026)
    tomorrow = datetime.now() + timedelta(days=1)
    date_str_1 = tomorrow.strftime("%b %d, %Y") # e.g., Sep 03, 2026
    date_str_2 = tomorrow.strftime("%Y-%m-%d")   # e.g., 2026-09-03
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, matchType, date, status 
        FROM upcoming_matches 
        WHERE date LIKE ? OR date LIKE ?
    """, (f"%{date_str_1}%", f"%{date_str_2}%"))
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n=======================================================")
    print(f"📅 FIXTURES FOR TOMORROW ({date_str_1})")
    print(f"=======================================================")
    print(f"{'MATCH ID':<38} | {'STATUS':<20} | {'MATCH NAME'}")
    print("-" * 105)
    
    if not rows:
        print("No matches explicitly indexed for tomorrow in the current cache.")
    else:
        for row in rows:
            match_id, name, match_type, date, status = row
            print(f"{match_id:<38} | {str(status):<20} | {name}")

if __name__ == "__main__":
    print("🔄 Syncing latest fixtures from CricAPI...")
    if refresh_fixtures():
        print("✅ Database sync complete.")
    get_tomorrow_matches()
