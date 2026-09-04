"""
==============================================================================
SYNDICATE OS - TELEGRAM NOTIFIER DISPATCHER (syndicate_notifier.py)
Reads Final_Lineups_Mobile_Summary.txt and dispatches it directly to Telegram.
==============================================================================
"""

import os
import requests

BASE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
SUMMARY_FILE = os.path.join(BASE_DIR, "Final_Lineups_Mobile_Summary.txt")

# Configured from your BotFather credentials and user ID
BOT_TOKEN = "8942957322:AAF86-GixapC8Rs88Jcn-wWX6M-o-6SYWKE"
CHAT_ID = "8942186617"

def send_telegram_broadcast():
    if not os.path.exists(SUMMARY_FILE):
        print(f"[ERROR] Summary file not found at {SUMMARY_FILE}. Run syndicate_os.py first.")
        return

    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        report_content = f.read()

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Telegram has a 4096 character limit per message; split chunks if necessary
    max_length = 4000
    chunks = [report_content[i:i+max_length] for i in range(0, len(report_content), max_length)]

    for idx, chunk in enumerate(chunks, 1):
        payload = {
            "chat_id": CHAT_ID,
            "text": f"🏏 **SYNDICATE OS DISPATCH (Part {idx}/{len(chunks)})**\n\n```text\n{chunk}\n```",
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"[SUCCESS] Telegram broadcast part {idx} dispatched successfully.")
        else:
            print(f"[ERROR] Failed to send part {idx}: {response.text}")

if __name__ == "__main__":
    send_telegram_broadcast()
