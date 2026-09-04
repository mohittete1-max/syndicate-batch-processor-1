import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def populate_csv(filename, data):
    filepath = os.path.join(BASE_DIR, filename)
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    print(f"[SUCCESS] Populated {filename} with {len(df)} players.")

# Glasgow Cosmics vs Rotterdam Dockers (Match 169300)
gla_vs_rot_data = {
    "Player": [
        # Glasgow Cosmics
        "Liam Livingstone", "Jason Roy", "Josh Philippe", "George Munsey", "Jimmy Neesham", 
        "Moises Henriques", "Richie Berrington", "Lungi Ngidi", "Keshav Maharaj", "Paul van Meekeren", "Brad Currie",
        # Rotterdam Dockers
        "Heinrich Klaasen", "Faf du Plessis", "Ben McDermott", "Aneurin Donald", "David Wiese", 
        "Roelof van der Merwe", "Logan van Beek", "Anrich Nortje", "Ryan Klein", "Jasper Davidson", "Saqib Zulfiqar"
    ],
    "Team": [
        "GLA", "GLA", "GLA", "GLA", "GLA", "GLA", "GLA", "GLA", "GLA", "GLA", "GLA",
        "ROT", "ROT", "ROT", "ROT", "ROT", "ROT", "ROT", "ROT", "ROT", "ROT", "ROT"
    ],
    "Role": [
        "ALL", "BAT", "WK", "BAT", "ALL", "ALL", "BAT", "BOWL", "BOWL", "BOWL", "BOWL",
        "WK", "BAT", "WK", "BAT", "ALL", "ALL", "ALL", "BOWL", "BOWL", "BOWL", "ALL"
    ],
    "Salary": [
        10.5, 9.5, 9.0, 8.5, 9.0, 8.5, 8.0, 9.0, 8.5, 8.0, 7.5,
        10.5, 9.5, 8.5, 8.0, 9.0, 8.5, 8.5, 9.5, 8.0, 7.5, 8.0
    ],
    "Projection": [
        65.0, 48.0, 45.0, 35.0, 48.0, 40.0, 32.0, 46.0, 44.0, 35.0, 30.0,
        62.0, 50.0, 42.0, 34.0, 48.0, 40.0, 43.0, 49.0, 35.0, 28.0, 30.0
    ]
}

if __name__ == "__main__":
    target_file = "Glasgow_Cosmics_vs_Rotterdam_Dockers_169300.csv"
    
    if os.path.exists(os.path.join(BASE_DIR, target_file)):
        populate_csv(target_file, gla_vs_rot_data)
    else:
        print(f"[ERROR] Could not find {target_file}. Verify the filename in your directory.")
