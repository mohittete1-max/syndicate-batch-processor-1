import sqlite3

DB_PATH = r"C:\Users\User\OneDrive\Desktop\Cricket\cricket_analytics.db"

def list_upcoming_matches():
    """Lists the next upcoming matches sorted by date."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, date, status 
        FROM upcoming_matches 
        WHERE date >= '2026-09-02'
        ORDER BY date ASC
        LIMIT 10
    """)
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n=======================================================")
    print(f"📅 NEXT UPCOMING MATCHES IN PIPELINE")
    print(f"=======================================================")
    print(f"{'DATE':<12} | {'STATUS':<30} | {'MATCH NAME'}")
    print("-" * 90)
    
    if not rows:
        print("No upcoming matches found in database.")
    else:
        for row in rows:
            match_id, name, date, status = row
            print(f"{str(date):<12} | {str(status):<30} | {name}")

if __name__ == "__main__":
    list_upcoming_matches()
