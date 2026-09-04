import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def populate_csv(filename, data):
    filepath = os.path.join(BASE_DIR, filename)
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    print(f"[SUCCESS] Populated {filename} with {len(df)} players.")

# ==========================================
# 1. South Africa vs Zimbabwe (Match 170000)
# ==========================================
sa_vs_zim_data = {
    "Player": [
        "Quinton de Kock", "Reeza Hendricks", "Aiden Markram", "Heinrich Klaasen", "David Miller", 
        "Tristan Stubbs", "Marco Jansen", "Keshav Maharaj", "Kagiso Rabada", "Anrich Nortje", "Tabraiz Shamsi",
        "Sikandar Raza", "Craig Ervine", "Sean Williams", "Ryan Burl", "Clive Madande", 
        "Wessly Madhevere", "Luke Jongwe", "Richard Ngarava", "Blessing Muzarabani", "Tendai Chatara", "Wellington Masakadza"
    ],
    "Team": [
        "SA", "SA", "SA", "SA", "SA", "SA", "SA", "SA", "SA", "SA", "SA",
        "ZIM", "ZIM", "ZIM", "ZIM", "ZIM", "ZIM", "ZIM", "ZIM", "ZIM", "ZIM", "ZIM"
    ],
    "Role": [
        "WK", "BAT", "ALL", "WK", "BAT", "BAT", "ALL", "BOWL", "BOWL", "BOWL", "BOWL",
        "ALL", "BAT", "ALL", "ALL", "WK", "ALL", "BOWL", "BOWL", "BOWL", "BOWL", "BOWL"
    ],
    "Salary": [
        9.5, 8.5, 9.5, 9.0, 8.5, 8.0, 9.0, 8.5, 9.0, 8.5, 8.0,
        10.0, 8.5, 9.0, 8.5, 8.0, 8.0, 7.5, 8.0, 8.5, 7.5, 7.0
    ],
    "Projection": [
        55.0, 42.0, 58.0, 48.0, 40.0, 38.0, 52.0, 45.0, 50.0, 46.0, 40.0,
        65.0, 40.0, 48.0, 42.0, 35.0, 38.0, 32.0, 38.0, 42.0, 30.0, 25.0
    ]
}

# ==========================================
# 2. Sri Lanka Women vs UAE Women (Match 169812)
# ==========================================
slw_vs_uaew_data = {
    "Player": [
        "Chamari Athapaththu", "Harshitha Samarawickrama", "Vishmi Gunaratne", "Hasini Perera", "Nilakshi de Silva", 
        "Kavisha Dilhari", "Anushka Sanjeewani", "Sugandika Kumari", "Inoshi Priyadharshani", "Udeshika Prabodhani", "Achini Kulasuriya",
        "Esha Oza", "Theertha Satish", "Kavisha Egodage", "Khushi Sharma", "Chaya Mughal", 
        "Samaira Dharnidharka", "Vaishnave Mahesh", "Suraksha Kotte", "Heena Hotchandani", "Indhuja Nandakumar", "Rinitha Rajith"
    ],
    "Team": [
        "SL-W", "SL-W", "SL-W", "SL-W", "SL-W", "SL-W", "SL-W", "SL-W", "SL-W", "SL-W", "SL-W",
        "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W", "UAE-W"
    ],
    "Role": [
        "ALL", "BAT", "BAT", "BAT", "BAT", "ALL", "WK", "BOWL", "BOWL", "BOWL", "BOWL",
        "ALL", "WK", "BAT", "ALL", "ALL", "ALL", "BOWL", "BOWL", "BOWL", "BOWL", "BAT"
    ],
    "Salary": [
        10.5, 8.5, 8.0, 8.0, 8.0, 9.0, 8.5, 8.5, 8.0, 8.5, 7.5,
        10.0, 9.0, 8.5, 8.5, 8.5, 8.0, 8.0, 7.5, 8.5, 8.0, 7.5
    ],
    "Projection": [
        75.0, 45.0, 35.0, 32.0, 30.0, 50.0, 42.0, 44.0, 38.0, 40.0, 30.0,
        65.0, 52.0, 40.0, 42.0, 38.0, 35.0, 36.0, 30.0, 45.0, 38.0, 25.0
    ]
}

if __name__ == "__main__":
    print("[SYSTEM] Injecting active player pool data into staging files...")
    populate_csv("South_Africa_vs_Zimbabwe_170000.csv", sa_vs_zim_data)
    populate_csv("Sri_Lanka_Women_vs_UAE_Women_169812.csv", slw_vs_uaew_data)
