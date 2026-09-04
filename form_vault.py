import sqlite3
import random
from datetime import datetime

def update_player_form():
    # Connect to your existing permanent vault
    conn = sqlite3.connect('global_cricket_vault.db')
    cursor = conn.cursor()
    
    # Create the Player Form table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_form_log (
            player_name TEXT PRIMARY KEY,
            role TEXT,
            recent_scores TEXT,
            avg_form_rating REAL,
            last_updated DATETIME
        )
    ''')
    
    # ---------------------------------------------------------
    # Simulated Live Scraper (In the future, this hooks to an API)
    # ---------------------------------------------------------
    print("Scraping last 5 matches for CPL Player Pool...")
    
    scraped_players = [
        {"name": "Andries Gous", "role": "BAT", "scores": [45, 12, 89, 0, 32]},
        {"name": "Roston Chase", "role": "AR", "scores": [22, 50, 15, 10, 5]},
        {"name": "Matthew Forde", "role": "BOWL", "scores": [0, 0, 10, 5, 20]},
        {"name": "Faf du Plessis", "role": "BAT", "scores": [75, 10, 5, 88, 41]},
        {"name": "Alzarri Joseph", "role": "BOWL", "scores": [0, 12, 0, 25, 0]}
    ]
    
    # Calculate averages and inject into the SQL Vault
    for p in scraped_players:
        avg_rating = sum(p["scores"]) / len(p["scores"])
        scores_str = ", ".join(map(str, p["scores"]))
        
        cursor.execute('''
            INSERT OR REPLACE INTO player_form_log 
            (player_name, role, recent_scores, avg_form_rating, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (p["name"], p["role"], scores_str, avg_rating, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()
    
    print("✅ Player Form Vault updated successfully. AI Engine now has form ratings.")

if __name__ == "__main__":
    update_player_form()
