import sqlite3

DB_PATH = r"C:\Users\User\OneDrive\Desktop\Cricket\cricket_analytics.db"

def view_stored_fixtures():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, matchType, date, status FROM upcoming_matches LIMIT 10")
    rows = cursor.fetchall()
    
    print(f"{'MATCH ID':<12} | {'STATUS':<15} | {'MATCH NAME'}")
    print("-" * 60)
    for row in rows:
        match_id, name, match_type, date, status = row
        print(f"{match_id:<12} | {str(status):<15} | {name}")
        
    conn.close()

if __name__ == "__main__":
    view_stored_fixtures()
