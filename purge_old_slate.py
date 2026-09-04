import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Completely delete the conflicting Rotterdam file if it still exists
old_file = os.path.join(BASE_DIR, "Glasgow_Cosmics_vs_Rotterdam_Dockers_169300.csv")
if os.path.exists(old_file):
    os.remove(old_file)
    print(f"[DELETED] Successfully removed obsolete file: {os.path.basename(old_file)}")

# 2. Generate the fresh, correct Dublin Guardians slate CSV
correct_file = os.path.join(BASE_DIR, "Glasgow_Cosmics_vs_Dublin_Guardians_169300.csv")
print(f"[CREATE] Generating clean slate: {os.path.basename(correct_file)}")

glasgow_vs_dublin_data = {
    "Player": [
        "George Munsey", "Jason Roy", "Matthew Cross", "Liam Livingstone", "Moises Henriques", 
        "Richie Berrington", "Michael Leask", "Keshav Maharaj", "Ali Khan", "Paul van Meekeren", "Lungi Ngidi",
        "Harry Tector", "Muhammad Waseem", "Sanjay Krishnamurthi", "Daryl Mitchell", "Vijay Shankar", 
        "Benjamin Calitz", "George Dockrell", "Ravichandran Ashwin", "Chris Wood", "Joshua Little", "Craig Young"
    ],
    "Role": [
        "BAT", "BAT", "WK", "ALL", "ALL", 
        "BAT", "ALL", "BOWL", "BOWL", "BOWL", "BOWL",
        "BAT", "BAT", "BAT", "ALL", "ALL", 
        "WK", "ALL", "ALL", "BOWL", "BOWL", "BOWL"
    ],
    "Team": [
        "Glasgow Cosmics", "Glasgow Cosmics", "Glasgow Cosmics", "Glasgow Cosmics", "Glasgow Cosmics",
        "Glasgow Cosmics", "Glasgow Cosmics", "Glasgow Cosmics", "Glasgow Cosmics", "Glasgow Cosmics", "Glasgow Cosmics",
        "Dublin Guardians", "Dublin Guardians", "Dublin Guardians", "Dublin Guardians", "Dublin Guardians",
        "Dublin Guardians", "Dublin Guardians", "Dublin Guardians", "Dublin Guardians", "Dublin Guardians", "Dublin Guardians"
    ],
    "Salary": [
        9.0, 9.5, 8.5, 10.5, 9.0, 
        8.5, 8.5, 8.5, 8.0, 8.0, 9.0,
        9.0, 9.0, 8.0, 9.5, 8.5, 
        8.5, 8.5, 9.5, 8.0, 8.5, 8.0
    ],
    "Projection": [
        45.0, 48.0, 42.0, 65.0, 44.0, 
        40.0, 40.0, 45.0, 38.0, 35.0, 46.0,
        46.0, 44.0, 38.0, 48.0, 40.0, 
        42.0, 45.0, 50.0, 40.0, 40.0, 38.0
    ]
}

df_new = pd.DataFrame(glasgow_vs_dublin_data)
df_new.to_csv(correct_file, index=False)
print("[SUCCESS] Glasgow Cosmics vs Dublin Guardians CSV is now active and error-free.")
