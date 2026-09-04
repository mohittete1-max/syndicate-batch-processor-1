import sqlite3

DB_PATH = r"C:\Users\User\OneDrive\Desktop\Cricket\cricket_analytics.db"

def insert_manual_matches():
    """Manually inserts today's live/ongoing and tomorrow's target matches into the SQLite fixture cache."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    manual_fixtures = [
        (
            "manual-slw-inaw-2026-09-02", 
            "Sri Lanka Women vs Indonesia Women, Match 6, Womens T20 Asia Cup 2026", 
            "T20I", 
            "2026-09-02", 
            "Dubai International Cricket Stadium", 
            "Innings Break"
        ),
        (
            "manual-engw-irew-2026-09-02", 
            "England Women vs Ireland Women", 
            "T20I", 
            "2026-09-02", 
            "England", 
            "Match Live / Upcoming"
        ),
        (
            "manual-nam-zim-2026-09-03", 
            "Namibia vs Zimbabwe, 5th T20I, Namibia T20I Tri-Series 2026", 
            "T20I", 
            "2026-09-03", 
            "Namibia Cricket Ground, Windhoek", 
            "Match starts at Sep 03, 17:30 IST"
        ),
        (
            "manual-indw-hkw-2026-09-03", 
            "India Women vs Hong Kong Women, Match 7, Womens T20 Asia Cup 2026", 
            "T20I", 
            "2026-09-03", 
            "Dubai International Cricket Stadium", 
            "Match starts at Sep 03, 20:00 IST"
        )
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO upcoming_matches (id, name, matchType, date, venue, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, manual_fixtures)
    
    conn.commit()
    conn.close()
    print("✅ Successfully updated SQLite with today's live matches and tomorrow's manual fixtures.")

if __name__ == "__main__":
    insert_manual_matches()
