import sqlite3

DB_PATH = r"C:\Users\User\OneDrive\Desktop\Cricket\cricket_analytics.db"

def inspect_all_fixtures():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, date, status FROM upcoming_matches")
    rows = cursor.fetchall()
    
    print(f"{'DATE FIELD':<25} | {'STATUS':<30} | {'MATCH NAME'}")
    print("-" * 90)
    for row in rows:
        match_id, name, date, status = row
        print(f"{str(date):<25} | {str(status):<30} | {name}")
        
    conn.close()

if __name__ == "__main__":
    print("Inspecting all cached match dates...")
    inspect_all_fixtures()
