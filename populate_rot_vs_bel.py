import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def populate_csv(filename, data):
    filepath = os.path.join(BASE_DIR, filename)
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    print(f"[SUCCESS] Populated {filename} with {len(df)} players.")

# ========================================================
# Rotterdam Dockers vs Belfast Wolves (Match 169288)
# ========================================================
rot_vs_bel_data = {
    "Player": [
        # Rotterdam Dockers
        "Heinrich Klaasen", "Faf du Plessis", "Ben McDermott", "Aneurin Donald", "David Wiese", 
        "Roelof van der Merwe", "Logan van Beek", "Anrich Nortje", "Ryan Klein", "Jasper Davidson", "Saqib Zulfiqar",
        # Belfast Wolves
        "Paul Stirling", "Harry Tector", "Lorcan Tucker", "Curtis Campher", "Mark Adair", 
        "Gareth Delany", "Ross Adair", "Barry McCarthy", "Craig Young", "Matthew Humphreys", "Neil Rock"
    ],
    "Team": [
        "ROT", "ROT", "ROT", "ROT", "ROT", "ROT", "ROT", "ROT", "ROT", "ROT", "ROT",
        "BEL", "BEL", "BEL", "BEL", "BEL", "BEL", "BEL", "BEL", "BEL", "BEL", "BEL"
    ],
    "Role": [
        "WK", "BAT", "WK", "BAT", "ALL", "ALL", "ALL", "BOWL", "BOWL", "BOWL", "ALL",
        "BAT", "BAT", "WK", "ALL", "ALL", "ALL", "BAT", "BOWL", "BOWL", "BOWL", "WK"
    ],
    "Salary": [
        10.5, 9.5, 8.5, 8.0, 9.0, 8.5, 8.5, 9.5, 8.0, 7.5, 8.0,
        9.5, 9.0, 8.5, 9.0, 9.5, 8.0, 7.5, 8.5, 8.0, 7.5, 7.5
    ],
    "Projection": [
        62.0, 50.0, 42.0, 34.0, 48.0, 40.0, 43.0, 49.0, 35.0, 28.0, 30.0,
        48.0, 46.0, 42.0, 52.0, 55.0, 36.0, 28.0, 40.0, 38.0, 32.0, 25.0
    ]
}

if __name__ == "__main__":
    populate_csv("Rotterdam_Dockers_vs_Belfast_Wolves_169288.csv", rot_vs_bel_data)
