import requests
import sqlite3

API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
DB_PATH = r"C:\Users\User\OneDrive\Desktop\Cricket\cricket_analytics.db"

def fetch_and_store_all_fixtures():
    """Paginates through CricAPI to pull a comprehensive list of fixtures."""
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
    
    total_inserted = 0
    # Loop through multiple pages (offsets 0, 25, 50, etc.)
    for offset in range(0, 75, 25):
        url = f"https://api.cricapi.com/v1/matches?apikey={API_KEY}&offset={offset}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                break
                
            payload = response.json()
            if payload.get("status") != "success":
                break
                
            matches = payload.get("data", [])
            if not matches:
                break
                
            for match in matches:
                cursor.execute("""
                    INSERT OR REPLACE INTO upcoming_matches (id, name, matchType, date, venue, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    match.get("id"),
                    match.get("name"),
                    match.get("matchType"),
                    match.get("date"),
                    match.get("venue"),
                    match.get("status")
                ))
                total_inserted += 1
                
        except Exception as e:
            print(f"Error at offset {offset}: {e}")
            break
            
    conn.commit()
    conn.close()
    print(f"Successfully synchronized {total_inserted} total fixtures into SQLite.")

if __name__ == "__main__":
    print("🔄 Pulling expanded fixture feed from CricAPI...")
    fetch_and_store_all_fixtures()
