import os
import requests

# ==============================================================================
# GLOBAL MATCH CODE EXTRACTOR
# ==============================================================================
# Using your verified CricData key
API_KEY = "4905f024-424c-4f6c-a2e6-b4e64f41f7bb"
BASE_URL = "https://api.cricapi.com/v1/matches"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def dump_all_match_codes():
    print("\n[SYSTEM] Paging through CricData to extract all match codes...")
    
    all_matches = []
    
    # Loop through the first 4 pages (100 upcoming/current matches)
    for offset in [0, 25, 50, 75]:
        params = {
            "apikey": API_KEY,
            "offset": offset
        }
        
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") != "success":
                print(f"  [WARN] Failed at offset {offset}. Stopping pagination.")
                break
                
            for match in data.get("data", []):
                # Prevent duplicates
                if match.get("id") not in [m['id'] for m in all_matches]:
                    all_matches.append({
                        "date": match.get("date", "Unknown Date"),
                        "name": match.get("name", "Unknown Match Name"),
                        "id": match.get("id", "Unknown ID")
                    })
                    
        except Exception as e:
            print(f"  [ERROR] Network error at offset {offset}: {e}")
            break

    if not all_matches:
        print("\n[ERROR] No matches retrieved. Check API key limits.")
        return

    # Write the full board to a text file for easy searching
    output_file = os.path.join(BASE_DIR, "available_match_codes.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("====================================================================================\n")
        f.write("                     CRICDATA GLOBAL MATCH CODES DIRECTORY\n")
        f.write("====================================================================================\n")
        f.write(f"{'DATE':<15} | {'MATCH ID':<38} | {'MATCH NAME'}\n")
        f.write("-" * 84 + "\n")
        
        for m in all_matches:
            # Also print to terminal
            print(f"[{m['date']}] {m['name']} -> ID: {m['id']}")
            
            # Write to file
            f.write(f"{m['date']:<15} | {m['id']:<38} | {m['name']}\n")
            
    print("\n" + "=" * 65)
    print(f"[SUCCESS] {len(all_matches)} match codes extracted!")
    print(f"[SAVED] Open 'available_match_codes.txt' in your Cricket folder.")

if __name__ == "__main__":
    dump_all_match_codes()
