import sqlite3

DB_PATH = r"C:\Users\User\OneDrive\Desktop\Cricket\cricket_analytics.db"

def get_today_matches():
    """Queries SQLite for matches scheduled for today (September 2, 2026)."""
    target_date = "2026-09-02"
    
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
    print(f"📅 MATCHES SCHEDULED FOR TODAY ({target_date})")
    print(f"=======================================================")
    print(f"{'MATCH ID':<38} | {'STATUS':<20} | {'MATCH NAME'}")
    print("-" * 105)
    
    if not rows:
        print(f"No matches scheduled for today ({target_date}) in the database cache.")
    else:
        for row in rows:
            match_id, name, match_type, date, status = row
            print(f"{match_id:<38} | {str(status):<20} | {name}")

if __name__ == "__main__":
    get_today_matches()
