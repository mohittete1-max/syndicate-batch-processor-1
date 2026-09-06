import os
import pandas as pd

# Use a relative path so it works both locally and inside the Docker container
DATA_DIR = "CRICSHEET DATA"
OUTPUT_FILE = "master_cricket_dataset.csv"

def parse_cricsheet_csv_directory(data_dir):
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Directory not found: '{data_dir}'. Ensure the 'CRICSHEET DATA' folder exists in your project root and is copied into the Docker image.")

    # 1. Check for the consolidated all_matches.csv first to speed up the process
    consolidated_path = os.path.join(data_dir, "all_matches.csv")
    
    if os.path.exists(consolidated_path):
        print(f"Found consolidated file: {consolidated_path}. Loading directly...")
        df = pd.read_csv(consolidated_path, low_memory=False)
        print(f"Loaded {len(df)} rows from all_matches.csv.")
        
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Saved master dataset to {OUTPUT_FILE}")
        return

    # 2. If no consolidated file is found, process the individual match CSVs
    print(f"Scanning directory '{data_dir}' for match files...")
    match_files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and not f.endswith('_info.csv')]
    
    if not match_files:
        raise ValueError(f"No match CSV files found in '{data_dir}'.")

    print(f"Found {len(match_files)} match files. Consolidating...")
    
    df_list = []
    for file in match_files:
        file_path = os.path.join(data_dir, file)
        try:
            temp_df = pd.read_csv(file_path, low_memory=False)
            df_list.append(temp_df)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            
    if not df_list:
        raise RuntimeError("Failed to load any data.")
        
    master_df = pd.concat(df_list, ignore_index=True)
    print(f"Loaded {len(master_df)} rows from individual files.")
    
    master_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved master dataset to {OUTPUT_FILE}")

if __name__ == "__main__":
    parse_cricsheet_csv_directory(DATA_DIR)
