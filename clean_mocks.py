import os
import pandas as pd

def clean_dummy_files():
    dummy_files = [
        "live_slate.csv", 
        "vegas_adjusted_slate.csv", 
        "weather_and_vegas_adjusted_slate.csv"
    ]
    for file in dummy_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed legacy dummy file: {file}")

if __name__ == "__main__":
    clean_dummy_files()
