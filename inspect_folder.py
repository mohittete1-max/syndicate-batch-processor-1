import pandas as pd
import glob

print("Scanning for CSV files...")
for file in glob.glob("*.csv"):
    try:
        df = pd.read_csv(file)
        print(f"\nFile: {file}")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print(f"\nFile: {file} (Could not read: {e})")
