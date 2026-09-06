import os
import pandas as pd

def parse_cricsheet_csv_directory(data_dir, output_csv="master_cricket_dataset.csv"):
    """
    Parses Cricsheet CSV data from the provided directory, 
    saves it to a master dataset CSV file for downstream pipelines.
    """
    all_matches_path = os.path.join(data_dir, "all_matches.csv")
    
    if os.path.exists(all_matches_path):
        print(f"Found consolidated file: {all_matches_path}. Loading directly...")
        df = pd.read_csv(all_matches_path, low_memory=False)
        print(f"Loaded {len(df)} rows from all_matches.csv.")
        
        # Save out to the expected master dataset filename
        df.to_csv(output_csv, index=False)
        print(f"Saved master dataset to {output_csv}")
        return df
        
    match_files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and not f.endswith('_info.csv')]
    print(f"Found {len(match_files)} individual match CSV files to process.")
    
    frames = []
    for file_name in match_files:
        file_path = os.path.join(data_dir, file_name)
        info_path = os.path.join(data_dir, file_name.replace('.csv', '_info.csv'))
        
        try:
            df_ball = pd.read_csv(file_path, low_memory=False)
            if os.path.exists(info_path):
                df_info = pd.read_csv(info_path, low_memory=False)
                for col in df_info.columns:
                    if col not in df_ball.columns:
                        df_ball[col] = df_info[col].iloc[0] if not df_info.empty else 'unknown'
                        
            frames.append(df_ball)
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            
    if frames:
        master_df = pd.concat(frames, ignore_index=True)
        master_df.to_csv(output_csv, index=False)
        print(f"Consolidated dataset saved to {output_csv} with {len(master_df)} rows.")
        return master_df
    else:
        print("No valid CSV match files found.")
        return None

if __name__ == "__main__":
    DATA_DIR = "C:/Users/User/OneDrive/Desktop/Cricket/CRICSHEET DATA"
    parse_cricsheet_csv_directory(DATA_DIR)
