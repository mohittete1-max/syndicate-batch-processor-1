import json
import pandas as pd
from pathlib import Path
import concurrent.futures
import time

def parse_cricsheet_json(file_path: Path) -> list:
    """Parses a single Cricsheet JSON and returns a list of row dictionaries."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    info = data.get('info', {})
    match_id = file_path.stem
    match_date = info.get('dates', [None])[0]
    venue = info.get('venue', 'Unknown')
    match_type = info.get('match_type', 'Unknown')
    
    records = []
    
    for innings in data.get('innings', []):
        batting_team = innings.get('team')
        
        for over_data in innings.get('overs', []):
            over_num = over_data.get('over')
            
            for ball_idx, delivery in enumerate(over_data.get('deliveries', [])):
                runs = delivery.get('runs', {})
                wickets = delivery.get('wickets', [])
                
                row = {
                    'match_id': match_id,
                    'date': match_date,
                    'match_type': match_type,
                    'venue': venue,
                    'batting_team': batting_team,
                    'over': over_num,
                    'ball': ball_idx + 1,
                    'batter': delivery.get('batter'),
                    'bowler': delivery.get('bowler'),
                    'runs_batter': runs.get('batter', 0),
                    'is_wicket': 1 if wickets else 0
                }
                records.append(row)
                
    return records

def compile_master_dataset(source_folder="data/raw/all_matches", output_csv="master_deliveries.csv"):
    """Finds all JSONs, parses them in parallel, and exports a master Pandas DataFrame."""
    source_path = Path(source_folder)
    json_files = list(source_path.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {source_folder}.")
        return

    print(f"Found {len(json_files)} match files. Starting parallel processing...")
    start_time = time.time()
    
    all_records = []
    
    # Process files in parallel using CPU cores
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(parse_cricsheet_json, json_files)
        
        for i, match_records in enumerate(results, 1):
            all_records.extend(match_records)
            if i % 1000 == 0:
                print(f"Processed {i}/{len(json_files)} matches...")

    print("Compiling into Pandas DataFrame...")
    df = pd.DataFrame(all_records)
    
    print(f"Exporting {len(df)} total deliveries to {output_csv}...")
    df.to_csv(output_csv, index=False)
    
    elapsed = time.time() - start_time
    print(f"Success! Master dataset generated in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    compile_master_dataset()
