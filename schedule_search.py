import requests

# ==============================================================================
# UPCOMING SCHEDULE SEARCH UTILITY
# ==============================================================================
API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
BASE_URL = "https://api.cricapi.com/v1/matches"

# The keywords for the specific slates we want to attack tomorrow
TARGET_KEYWORDS = ["Zimbabwe", "South Africa", "Sri Lanka", "UAE", "Glasgow", "Dublin", "Rotterdam", "Belfast"]

def search_upcoming_schedule():
    print(f"\n--> Paging through CricData Schedule for targeted slates...")
    
    found_matches = []
    
    # Loop through the first 4 pages of the API (offset 0, 25, 50, 75)
    for offset in [0, 25, 50, 75]:
        params = {
            "apikey": API_KEY,
            "offset": offset
        }
        
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") != "success":
                continue
                
            for match in data.get("data", []):
                match_name = match.get("name", "").lower()
                
                # If any of our target keywords are in the match name, save it
                if any(term.lower() in match_name for term in TARGET_KEYWORDS):
                    # Prevent duplicates just in case
                    if match.get("id") not in [m['id'] for m in found_matches]:
                        found_matches.append({
                            "date": match.get("date", "Unknown"),
                            "name": match.get("name", "Unknown Match"),
                            "id": match.get("id", "Unknown ID")
                        })
                        
        except Exception as e:
            print(f"  [ERROR] Network error at offset {offset}: {e}")
            break

    if not found_matches:
        print("\n  [INFO] No matches found matching your keywords in the upcoming schedule.")
        return

    print("\n[SUCCESS] Found targeted fixtures:\n")
    print(f"{'Date':<15} {'Match Name':<50} {'Match ID'}")
    print("-" * 105)
    
    for m in found_matches:
        print(f"{m['date']:<15} {m['name']:<50} {m['id']}")
            
    print("\n" + "=" * 105)
    print("Copy these Match IDs directly into the TARGET_FIXTURES block in your batch_extractor.py script!")

if __name__ == "__main__":
    search_upcoming_schedule()
