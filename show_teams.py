import os
import pandas as pd

def display_all_archived_teams():
    """Locates the archive folder, reads all match rosters, and displays parsed team rosters."""
    archive_dir = r"C:\Users\User\OneDrive\Desktop\Cricket\archived_match_rosters"
    
    if not os.path.exists(archive_dir):
        print(f"[ERROR] Directory '{archive_dir}' does not exist.")
        print(f"Please run 'archive_generator.py' first.")
        return
        
    files = [f for f in os.listdir(archive_dir) if f.endswith("_roster.csv")]
    
    if not files:
        print(f"[WARNING] No archived roster CSVs found inside {archive_dir}.")
        return
        
    for file in files:
        file_path = os.path.join(archive_dir, file)
        df = pd.read_csv(file_path)
        
        match_title = df["match_target"].iloc[0] if "match_target" in df.columns else file
        
        # Check for column variance ('projected' vs 'projected_points')
        proj_col = "projected" if "projected" in df.columns else "projected_points"
        
        print("=" * 60)
        print(f"MATCH: {match_title}")
        print("-" * 60)
        print(df[["player_name", "role", "credits", proj_col]].to_string(index=False))
        print("=" * 60 + "\n")

if __name__ == "__main__":
    display_all_archived_teams()
