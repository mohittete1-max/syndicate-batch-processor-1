import pandas as pd
import difflib

csv_file = "THA_W_vs_HK_W.csv"

# The exact 22 starters from the live toss announcement
official_xi = [
    "Mariko Hill", "Yasmin Daswani", "Maryam Bibi", "Marina Lamplough", "Kary Chan", 
    "Shanzeen Shahzad", "Joyleen Kaur", "Shing Chan Dorothea", "Alison Siu", 
    "Charlotte Chan", "Ruchitha Venkatesh",
    "Naruemol Chaiwai", "Nannapat Koncharoenkai", "Chanida Sutthiruang", "Naomi Hamilton", 
    "Onnicha Kamchomphu", "Thipatcha Putthawong", "Phannita Maya", "Nannaphat Chaihan", 
    "Suleeporn Laomi", "Aphisara Suwanchonrathi", "Sunida Chaturongrattana"
]

def lock_official_xi():
    print("=================================================================")
    print("         HARDCODED TOSS OVERRIDE: THA W vs HK W                  ")
    print("=================================================================")
    
    try:
        df = pd.read_csv(csv_file)
        
        # Ensure column exists, then bench everyone by default
        if 'is_playing' not in df.columns:
            df['is_playing'] = 0
        df['is_playing'] = 0 
        
        csv_names = df['player_name'].tolist()
        matched_count = 0
        
        for official_name in official_xi:
            # 1. Try fuzzy match
            matches = difflib.get_close_matches(official_name, csv_names, n=1, cutoff=0.45)
            if matches:
                df.loc[df['player_name'] == matches[0], 'is_playing'] = 1
                matched_count += 1
            else:
                # 2. Try last-name fallback if spelling differs wildly
                last_name = official_name.split()[-1].lower()
                for c_name in csv_names:
                    if last_name in c_name.lower():
                        df.loc[df['player_name'] == c_name, 'is_playing'] = 1
                        matched_count += 1
                        break
                        
        df.to_csv(csv_file, index=False)
        print(f"[SUCCESS] Updated {csv_file}. {matched_count}/22 players locked as active.")
        print("--> You can now run 'batch_pipeline.py' to get the final lineup.")
        print("=================================================================")
        
    except FileNotFoundError:
        print(f"[ERROR] Could not find {csv_file} in the current directory.")

if __name__ == "__main__":
    lock_official_xi()
