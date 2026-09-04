# telegram_test.py
import requests

# Your exact token from BotFather
TOKEN = "8939525053:AAETS86KY5ojo9Tf3eC1SfKKGbqgVYPJA8A" 

# Your exact Chat ID from userinfobot
CHAT_ID = "1432527576"

def send_test_alert():
    message = "🚨 Apex Alpha OS: Secure connection established! The quant desk is live."
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    
    print("Transmitting signal to mobile...")
    response = requests.get(url)
    
    if response.status_code == 200:
        print("Success! Check your phone.")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    send_test_alert()
