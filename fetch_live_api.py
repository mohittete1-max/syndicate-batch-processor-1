import pandas as pd
import requests

def fetch_upcoming_slate(api_key="YOUR_API_KEY_HERE", match_id="upcoming_match_123"):
    print("Connecting to Fantasy Sports API...")
    
    # In production, you will uncomment this to hit your CricData/EntitySport API
    # URL = f"https://api.cricdata.com/v1/fantasy-slate/{match_id}?apikey={api_key}"
    # response = requests.get(URL)
    # data = response.json()
    
    print("API connection simulated. Formatting live data...")
    
    # Simulated 20-man squad API response
    live_data = [
        {"player": "Virat Kohli", "team": "IND", "role": "BAT", "salary": 10.5, "projected_points": 72.5},
        {"player": "Rohit Sharma", "team": "IND", "role": "BAT", "salary": 10.0, "projected_points": 65.0},
        {"player": "Suryakumar Yadav", "team": "IND", "role": "BAT", "salary": 9.5, "projected_points": 60.0},
        {"player": "Hardik Pandya", "team": "IND", "role": "AR", "salary": 10.0, "projected_points": 68.0},
        {"player": "Jasprit Bumrah", "team": "IND", "role": "BOWL", "salary": 9.5, "projected_points": 70.0},
        {"player": "Ravindra Jadeja", "team": "IND", "role": "AR", "salary": 9.0, "projected_points": 55.0},
        {"player": "Rishabh Pant", "team": "IND", "role": "WK", "salary": 8.5, "projected_points": 50.0},
        {"player": "Arshdeep Singh", "team": "IND", "role": "BOWL", "salary": 8.0, "projected_points": 45.0},
        {"player": "Mohammed Siraj", "team": "IND", "role": "BOWL", "salary": 8.5, "projected_points": 48.0},
        {"player": "Jos Buttler", "team": "ENG", "role": "WK", "salary": 10.5, "projected_points": 75.0},
        {"player": "Jonny Bairstow", "team": "ENG", "role": "BAT", "salary": 9.5, "projected_points": 58.0},
        {"player": "Phil Salt", "team": "ENG", "role": "WK", "salary": 8.5, "projected_points": 49.0},
        {"player": "Moeen Ali", "team": "ENG", "role": "AR", "salary": 9.0, "projected_points": 52.0},
        {"player": "Liam Livingstone", "team": "ENG", "role": "AR", "salary": 9.0, "projected_points": 50.0},
        {"player": "Sam Curran", "team": "ENG", "role": "AR", "salary": 9.5, "projected_points": 62.0},
        {"player": "Jofra Archer", "team": "ENG", "role": "BOWL", "salary": 9.5, "projected_points": 65.0},
        {"player": "Adil Rashid", "team": "ENG", "role": "BOWL", "salary": 9.0, "projected_points": 55.0},
        {"player": "Mark Wood", "team": "ENG", "role": "BOWL", "salary": 8.5, "projected_points": 46.0},
        {"player": "Chris Jordan", "team": "ENG", "role": "BOWL", "salary": 8.0, "projected_points": 42.0},
        {"player": "Harry Brook", "team": "ENG", "role": "BAT", "salary": 8.5, "projected_points": 48.0}
    ]
    
    df = pd.DataFrame(live_data)
    df.to_csv("live_slate.csv", index=False)
    print("Success! live_slate.csv generated automatically.")

if __name__ == "__main__":
    fetch_upcoming_slate()
