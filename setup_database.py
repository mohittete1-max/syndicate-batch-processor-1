# setup_database.py - Apex Alpha OS: Global SQL Vault Initialization
import sqlite3
import os

def create_global_vault():
    print("Initiating Global Cricket Vault...")
    
    # Connect to SQLite (This creates the file if it doesn't exist in your Cricket folder)
    db_path = "global_cricket_vault.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create Global Players Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Global_Players (
        Player_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Player_Name TEXT UNIQUE NOT NULL,
        National_Team TEXT,
        Franchise_Team TEXT,
        Role TEXT,
        Base_Credits REAL
    )
    ''')
    print("[-] Global_Players table secured.")

    # 2. Create Global Venues Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Global_Venues (
        Venue_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Venue_Name TEXT UNIQUE NOT NULL,
        Country TEXT,
        Pitch_Profile TEXT,
        Meteo_Multiplier REAL,
        Favored_Role TEXT
    )
    ''')
    print("[-] Global_Venues table secured.")

    # 3. Create Syndicate Financial Ledger
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Syndicate_Ledger (
        Ledger_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Tournament_Name TEXT,
        Match_Name TEXT,
        Teams_Generated INTEGER,
        Total_Investment_INR REAL,
        Total_Return_INR REAL,
        Execution_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("[-] Syndicate_Ledger table secured.")

    # Commit changes and close the vault
    conn.commit()
    conn.close()
    print(f"✅ Vault Successfully Created: {os.path.abspath(db_path)}")

if __name__ == "__main__":
    create_global_vault()
