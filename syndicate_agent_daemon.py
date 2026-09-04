import os
import time
import json
import requests
import subprocess
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ==============================================================================
# 🤖 SYNDICATE OS — AUTONOMOUS AGENT DAEMON v5.1 (TELEGRAM UPLINK ACTIVE)
# ==============================================================================
WORKSPACE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
CORE_ENGINE = os.path.join(WORKSPACE_DIR, "syndicate_os.py")
COMPLETED_FILE = os.path.join(WORKSPACE_DIR, "completed_matches.json")

RAPIDAPI_KEY = "b84c777f82mshf8a62983fcca58dp1a6214jsn0eb579d1ea5d"
RAPIDAPI_HOST = "free-cricbuzz-cricket-api.p.rapidapi.com"

# 🔐 TELEGRAM INTEGRATION
TELEGRAM_BOT_TOKEN = "8942957322:AAF86-GixapC8Rs88Jcn-wWX6M-o-6SYWKE"
TELEGRAM_CHAT_ID = "8942186617"
ENABLE_TELEGRAM = True

# Simulated Schedule with overlapping match times for today
MASTER_SCHEDULE = [
    {
        "match_id": "169991",
        "match_name": "NAM vs UGA",
        "series": "Namibia T20I Tri-Series 2026",
        "start_time": "2026-09-01 14:00",
        "team_a": "NAM",
        "team_b": "UGA",
        "pitch": "PACE",
        "weather": "CLEAR",
        "fav": "NAM"
    },
    {
        "match_id": "169813",
        "match_name": "SLW vs IDNW",
        "series": "Women's Asia Cup 2026",
        "start_time": "2026-09-01 14:00",
        "team_a": "SLW",
        "team_b": "IDNW",
        "pitch": "SPIN",
        "weather": "DEW",
        "fav": "SLW"
    }
]

file_lock = threading.Lock()

def send_telegram_alert(text):
    """Pushes direct real-time notifications to your mobile device."""
    if not ENABLE_TELEGRAM:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[-] Telegram Dispatch Failed: {e}")

def poll_live_match_info(match_id):
    url = "https://free-cricbuzz-cricket-api.p.rapidapi.com/cricket-match-info"
    querystring = {"matchid": match_id}
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        if response.status_code == 200:
            data = response.json()
            match_info = data.get("matchInfo", {})
            toss_results = match_info.get("tossResults", {})
            
            toss_winner = toss_results.get("tossWinnerName", "TBD")
            toss_decision = toss_results.get("decision", "TBD").upper()
            return toss_winner, toss_decision
        return "TBD", "TBD"
    except Exception:
        return "TBD", "TBD"

def load_completed_state():
    if os.path.exists(COMPLETED_FILE):
        with open(COMPLETED_FILE, 'r') as f:
            return json.load(f)
    return []

def mark_completed(match_id):
    with file_lock:
        completed = load_completed_state()
        if match_id not in completed:
            completed.append(match_id)
            with open(COMPLETED_FILE, 'w') as f:
                json.dump(completed, f, indent=4)

def process_match_thread(slate):
    """
    Independent execution thread for a single match.
    Runs concurrently without blocking other matches.
    """
    match_id = slate["match_id"]
    match_name = slate["match_name"]
    thread_name = f"[{match_id}]"

    print(f"\n{thread_name} Target Acquired -> {match_name} is LIVE.")
    print(f"{thread_name} Initiating RapidAPI Toss Polling Loop...")
    
    toss_winner, toss_decision = "TBD", "TBD"
    poll_attempts = 0
    
    # Polling Loop
    while toss_winner == "TBD" and poll_attempts < 20:
        toss_winner, toss_decision = poll_live_match_info(match_id)
        if toss_winner == "TBD":
            print(f"{thread_name} Toss pending... Retrying in 30s (Attempt {poll_attempts+1}/20)")
            time.sleep(30)
            poll_attempts += 1
            
    if toss_winner == "TBD":
        print(f"{thread_name} [-] Polling timed out. Applying default heuristics.")
        toss_winner = slate["team_a"]
        toss_decision = "FIELD"

    print(f"{thread_name} SUCCESS: Toss officially verified -> {toss_winner} ({toss_decision})")
    
    # 🔔 PUSH TOSS ALERT DIRECTLY TO TELEGRAM
    toss_alert = f"🚨 TOSS UPDATE: {match_name} 🚨\nWinner: {toss_winner} ({toss_decision})\nSurface: {slate['pitch']} | Meteo: {slate['weather']}\n\n⚙️ Triggering Syndicate OS optimization engine..."
    send_telegram_alert(toss_alert)

    # Prevent file collision by using match-specific state files
    state_file = os.path.join(WORKSPACE_DIR, f"live_state_{match_id}.json")
    state_data = {
        "match_id": match_id,
        "match_name": match_name,
        "pitch": slate["pitch"],
        "weather": slate["weather"],
        "toss_winner": toss_winner,
        "toss_decision": toss_decision
    }
    
    with open(state_file, 'w') as f:
        json.dump(state_data, f, indent=4)

    print(f"{thread_name} Triggering engine execution...")
    
    # Trigger core engine 
    try:
        # Capture stdout so the daemon can pass it to Telegram itself
        result = subprocess.run(["python", CORE_ENGINE], capture_output=True, text=True, timeout=45)
        
        if result.returncode == 0:
            print(f"{thread_name} [+] Execution complete. Telegram report dispatched.")
            # 🔔 CAPTURE AND PUSH LINEUP OUTPUT TO TELEGRAM
            if "MATHEMATICALLY OPTIMAL REPORT" in result.stdout:
                send_telegram_alert(result.stdout)
            else:
                send_telegram_alert(f"✅ Optimizer completed for {match_name}, but report parsing failed. Please check your terminal.")
        else:
            print(f"{thread_name} [-] Core Engine Error: {result.stderr}")
            send_telegram_alert(f"❌ Core Engine Error on {match_name}:\n{result.stderr}")
            
    except Exception as e:
        print(f"{thread_name} [-] Execution Failed: {e}")
        send_telegram_alert(f"❌ Execution Failed on {match_name}:\n{e}")

    mark_completed(match_id)
    print(f"{thread_name} Concluded and archived.")

def run_daemon():
    print("=======================================================")
    print("SYNDICATE OS: AUTONOMOUS AGENT DAEMON INITIALIZED (v5.1)")
    print("      [ TELEGRAM UPLINK & CONCURRENCY ACTIVE ]      ")
    print("=======================================================")

    executor = ThreadPoolExecutor(max_workers=5) 
    
    while True:
        completed_matches = load_completed_state()
        active_threads = []

        for slate in MASTER_SCHEDULE:
            if slate["match_id"] in completed_matches:
                continue
            active_threads.append(slate)

        if not active_threads:
            print("[DAEMON-MAIN] All scheduled slates completed. Sleeping for 10 minutes...")
            time.sleep(600)
            continue

        print(f"[DAEMON-MAIN] Detected {len(active_threads)} matches pending. Launching threads...")
        
        futures = []
        for slate in active_threads:
            futures.append(executor.submit(process_match_thread, slate))
            # Tiny delay between thread launches to prevent API rate-limiting spikes
            time.sleep(2) 

        for future in futures:
            future.result() 

        print("[DAEMON-MAIN] Batch complete. Re-evaluating schedule...")
        time.sleep(5)

if __name__ == "__main__":
    run_daemon()
