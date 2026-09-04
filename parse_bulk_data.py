import json
import pandas as pd
from pathlib import Path

def parse_dfs_data(base_path="data/raw"):
    # Recursively find all JSON files across all subfolders (ipl, t20s, etc.)
    files = list(Path(base_path).rglob("*.json"))
    print(f"Discovered {len(files)} targeted matches. Parsing into memory...")
    
    rows = []
    for idx, file_path in enumerate(files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                match = json.load(f)
                
            match_id = file_path.stem
            
            # Extract match-level metadata
            info = match.get("info", {})
            date = info.get("dates", ["Unknown"])[0]
            teams = info.get("teams", ["Team A", "Team B"])
            
            # Extract ball-by-ball data
            for inning in match.get("innings", []):
                team_batting = inning.get("team")
                # Deduce bowling team
                team_bowling = teams[1] if team_batting == teams[0] else teams[0]
                
                for over in inning.get("overs", []):
                    over_num = over.get("over")
                    for ball in over.get("deliveries", []):
                        runs = ball.get("runs", {})
                        
                        rows.append({
                            "match_id": match_id,
                            "date": date,
                            "batting_team": team_batting,
                            "bowling_team": team_bowling,
                            "over": over_num,
                            "batter": ball.get("batter"),
                            "bowler": ball.get("bowler"),
                            "batter_runs": runs.get("batter", 0),
                            "extras": runs.get("extras", 0),
                            "is_wicket": 1 if "wickets" in ball else 0
                        })
                        
        except Exception as e:
            print(f"Skipping {file_path.name} due to error: {e}")
            
        if idx % 1000 == 0:
            print(f"Processed {idx}/{len(files)} matches...")

    # Export to the master dataset
    if rows:
        df = pd.DataFrame(rows)
        df.to_csv("master_deliveries.csv", index=False)
        print(f"Success! master_deliveries.csv generated with {len(df)} deliveries.")
    else:
        print("No data extracted. Check your JSON files.")

if __name__ == "__main__":
    parse_dfs_data()
