"""
==============================================================================
DREAMWEAVER OS - INTERACTIVE DREAM FANTASY SYSTEM (DreamWeaver OS.py)
Powered by OpenRouter / OX Alpha & SQLite Persistence
==============================================================================
"""

import os
import sqlite3
import requests

# ----- Configuration -----
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OX_ALPHA_KEY", "your-openrouter-or-ox-alpha-key")
MODEL = "google/gemini-2.5-pro"  # Adjust model slug as needed

DB_FILE = "dreams.db"

def init_db():
    """Initializes the SQLite database for dream persistence."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dreams (
            dream_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            history TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_dream_state(dream_id, title, history):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    history_json = json_dumps(history)
    cursor.execute("""
        INSERT OR REPLACE INTO dreams (dream_id, title, history)
        VALUES (?, ?, ?)
    """, (dream_id, title, history_json))
    conn.commit()
    conn.close()

import json
def json_dumps(obj):
    return json.dumps(obj)

def json_loads(s):
    return json.loads(s)

def ask_gemini(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://dreamweaver-os.local",
        "X-Title": "DreamWeaver OS - DFS"
    }
    
    payload = {
        "model": MODEL,
        "messages": messages
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[ERROR connecting to OX Alpha gateway]: {e}"

def run_cli():
    init_db()
    print("==================================================")
    print("       DREAMWEAVER OS - ACTIVE (DFS MODE)         ")
    print("==================================================")
    
    seed = input("\nEnter your dream seed (e.g., 'a city built entirely of floating glass'): ").strip()
    if not seed:
        seed = "a floating island above a sea of neon clouds"

    messages = [
        {"role": "system", "content": "You are an immersive Dream Guide for a Dream Fantasy System (DFS). Create vivid, atmospheric scenes (4-6 sentences) and always end with a distinct choice for the user."},
        {"role": "user", "content": f"Begin the dream based on this seed: {seed}"}
    ]

    print("\n[Dream Guide is weaving your reality...]\n")
    response = ask_gemini(messages)
    print(response)
    
    messages.append({"role": "assistant", "content": response})

    # Save initial state to SQLite
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dreams (title, history) VALUES (?, ?)", (seed[:30], json_dumps(messages)))
    dream_id = cursor.lastrowid
    conn.commit()
    conn.close()

    while True:
        action = input("\nWhat do you do? (type 'exit' to wake up): ").strip()
        if action.lower() in ["exit", "quit", "wake up"]:
            print("\nYou open your eyes. The dream fades into memory.")
            break
            
        messages.append({"role": "user", "content": action})
        
        print("\n[Dream Guide is processing your action...]\n")
        response = ask_gemini(messages)
        print(response)
        
        messages.append({"role": "assistant", "content": response})
        
        # Update SQLite persistence
        save_dream_state(dream_id, seed[:30], messages)

if __name__ == "__main__":
    run_cli()
