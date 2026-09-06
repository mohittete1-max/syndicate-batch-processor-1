import os
import pandas as pd
from pipeline_cricsheet_parser import parse_cricsheet_json
from pipeline_venue_profiler import get_venue_profile
from pipeline_weather_injector import calculate_dew_risk

def run_master_pipeline(cricsheet_dir, output_csv="master_cricket_dataset.csv"):
    """
    Orchestrates parsing of extracted Cricsheet JSON files, injects venue profiles,
    and appends meteorological adjustments into a single master dataset.
    """
    all_matches = []
    
    if not os.path.exists(cricsheet_dir):
        print(f"Directory not found: {cricsheet_dir}")
        return None
        
    files = [f for f in os.listdir(cricsheet_dir) if f.endswith('.json')]
    print(f"Found {len(files)} match files to process in {cricsheet_dir}.")
    
    for file_name in files:
        file_path = os.path.join(cricsheet_dir, file_name)
        try:
            df_match = parse_cricsheet_json(file_path)
            
            if not df_match.empty:
                venue_name = df_match['venue'].iloc[0]
                profile = get_venue_profile(venue_name)
                
                df_match['pitch_type'] = profile['pitch_type']
                df_match['boundary_factor'] = profile['boundary_size_factor']
                df_match['pace_wicket_share'] = profile['pace_wicket_share']
                df_match['spin_wicket_share'] = profile['spin_wicket_share']
                
                is_night = True  
                temp_c = 28.0
                humidity = 75.0
                df_match['dew_risk_score'] = calculate_dew_risk(temp_c, humidity, is_night)
                
                all_matches.append(df_match)
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            
    if all_matches:
        master_df = pd.concat(all_matches, ignore_index=True)
        master_df.to_csv(output_csv, index=False)
        print(f"Pipeline complete! Master dataset saved to {output_csv} with {len(master_df)} total rows.")
        return master_df
    else:
        print("No match data processed successfully.")
        return None

if __name__ == "__main__":
    DATA_DIR = "C:/Users/User/OneDrive/Desktop/Cricket/cricsheet data"
    run_master_pipeline(DATA_DIR)
