import sqlite3
import os

WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
DB_PATH = os.path.join(WORKSPACE_DIR, "cricket_analytics.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def push_actuals_to_db(match_id, actuals_df):
    """
    Pushes actual player performance scores and post-lock ownership metrics 
    into the local SQLite database after a match concludes.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ensure table exists locally
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_actuals (
        match_id TEXT,
        player_id TEXT,
        actual_pts REAL,
        actual_own REAL,
        PRIMARY KEY (match_id, player_id)
    )
    """)
    
    insert_query = """
    INSERT INTO player_actuals (match_id, player_id, actual_pts, actual_own)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(match_id, player_id) 
    DO UPDATE SET actual_pts = excluded.actual_pts,
                  actual_own = excluded.actual_own;
    """
    
    try:
        for _, row in actuals_df.iterrows():
            cursor.execute(insert_query, (
                str(match_id), 
                str(row['player_id']), 
                float(row['actual_pts']), 
                float(row['actual_own'])
            ))
        conn.commit()
        print(f"✅ Successfully updated player actuals for match {match_id} in SQLite.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Database ingestion failed: {e}")
    finally:
        cursor.close()
        conn.close()

def update_lineup_totals(lineup_id):
    """
    Calculates total points and ownership for a specific lineup entry 
    based on actual player performances and selected multipliers.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    update_query = """
    UPDATE lineup_entries 
    SET total_pts = sub.total_pts,
        total_own = sub.total_own
    FROM (
        SELECT 
            le.lineup_id,
            SUM(CASE WHEN lp.player_id = le.captain_id THEN pa.actual_pts * 2 ELSE pa.actual_pts END) AS total_pts,
            SUM(pa.actual_own) AS total_own
        FROM lineup_entries le
        JOIN lineup_players lp ON le.lineup_id = lp.lineup_id
        JOIN player_actuals pa ON lp.player_id = pa.player_id AND lp.match_id = le.match_id
        WHERE le.lineup_id = ?
        GROUP BY le.lineup_id
    ) sub
    WHERE lineup_entries.lineup_id = sub.lineup_id;
    """
    
    try:
        cursor.execute(update_query, (lineup_id,))
        conn.commit()
        print(f"✅ Lineup {lineup_id} totals updated successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Lineup update failed: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print(f"📂 Initialized local SQLite database at: {DB_PATH}")
