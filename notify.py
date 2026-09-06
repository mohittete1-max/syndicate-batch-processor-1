import os
import requests

def send_alert(message):
    token = "8942957322:AAF86-GixapC8Rs88Jcn-wWX6M-o-6SYWKE"
    chat_id = "8942186617"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("🔔 Telegram notification sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")

if __name__ == "__main__":
    send_alert("🚀 *DFS Pipeline Success!* Lineups generated and uploaded to GCP.")
