import requests

RAPIDAPI_KEY = "PASTE_YOUR_RAPIDAPI_KEY_HERE"
RAPIDAPI_HOST = "cricbuzz-cricket.p.rapidapi.com"

def run_diagnostic():
    print("Pinging Cricbuzz API for raw response...\n")
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print("Raw Server Response:")
    print(response.text)

if __name__ == "__main__":
    run_diagnostic()
