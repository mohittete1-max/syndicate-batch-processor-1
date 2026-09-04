import sqlite3
from datetime import datetime, timedelta

DB_PATH = r"C:\Users\User\OneDrive\Desktop\Cricket\cricket_analytics.db"

def get_tomorrow_matches():
    """Queries SQLite for matches scheduled for tomorrow using the YYYY-MM-DD format."""
    tomorrow = datetime.now() + timedelta(days=1)
    target_date = tomorrow.strftime("%Y-%m-%d") # e.g., 2026-09-03
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, matchType, date, status 
        FROM upcoming_matches 
        WHERE date = ?
    """, (target_date,))
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n=======================================================")
    print(f"📅 FIXTURES FOR TOMORROW ({target_date})")
    print(f"=======================================================")
    print(f"{'MATCH ID':<38} | {'STATUS':<20} | {'MATCH NAME'}")
    print("-" * 105)
    
    if not rows:
        print(f"No matches scheduled for {target_date} in the current database cache.")
    else:
        for row in rows:
            match_id, name, match_type, date, status = row
            print(f"{match_id:<38} | {str(status):<20} | {name}")

if __name__ == "__main__":
    get_tomorrow_matches()
