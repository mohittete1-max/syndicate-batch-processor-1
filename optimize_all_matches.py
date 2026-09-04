import sqlite3

DB_PATH = r"C:\Users\User\OneDrive\Desktop\Cricket\cricket_analytics.db"

# ==========================================
# 1. ENGLAND WOMEN vs IRELAND WOMEN POOL
# ==========================================
ENG_IRE_POOL = [
    {"name": "A Hunter", "role": "WK", "team": "IRE-W", "credits": 7.5, "points": 94},
    {"name": "Coulter Reilly", "role": "WK", "team": "IRE-W", "credits": 7.0, "points": 0},
    {"name": "K Chathli", "role": "WK", "team": "ENG-W", "credits": 6.5, "points": 0},
    {"name": "S Dunkley", "role": "BAT", "team": "ENG-W", "credits": 8.0, "points": 139},
    {"name": "M Bouchier", "role": "BAT", "team": "ENG-W", "credits": 6.0, "points": 178},
    {"name": "G Lewis", "role": "BAT", "team": "IRE-W", "credits": 8.5, "points": 113},
    {"name": "A Capsey", "role": "BAT", "team": "ENG-W", "credits": 8.0, "points": 81},
    {"name": "R Stokell", "role": "BAT", "team": "IRE-W", "credits": 7.5, "points": 96},
    {"name": "L Paul", "role": "BAT", "team": "IRE-W", "credits": 8.0, "points": 45},
    {"name": "A Tector", "role": "BAT", "team": "IRE-W", "credits": 7.0, "points": 31},
    {"name": "O Prendergast", "role": "AR", "team": "IRE-W", "credits": 9.0, "points": 75},
    {"name": "C Dean", "role": "AR", "team": "ENG-W", "credits": 7.0, "points": 113},
    {"name": "F Kemp", "role": "AR", "team": "ENG-W", "credits": 7.5, "points": 78},
    {"name": "A Kelly", "role": "AR", "team": "IRE-W", "credits": 7.5, "points": 53},
    {"name": "M Villiers", "role": "AR", "team": "ENG-W", "credits": 6.0, "points": 55},
    {"name": "D Gibson", "role": "AR", "team": "ENG-W", "credits": 6.0, "points": 19},
    {"name": "J Grewcock", "role": "AR", "team": "ENG-W", "credits": 7.0, "points": 17},
    {"name": "G Dempsey", "role": "AR", "team": "IRE-W", "credits": 7.0, "points": 0},
    {"name": "C Pavely", "role": "AR", "team": "ENG-W", "credits": 7.5, "points": 0},
    {"name": "C Murray", "role": "BOWL", "team": "IRE-W", "credits": 8.0, "points": 130},
    {"name": "I Wong", "role": "BOWL", "team": "ENG-W", "credits": 6.5, "points": 104},
    {"name": "L Filer", "role": "BOWL", "team": "ENG-W", "credits": 6.0, "points": 45},
    {"name": "L Little", "role": "BOWL", "team": "IRE-W", "credits": 7.5, "points": 17},
    {"name": "T Corteen-Coleman", "role": "BOWL", "team": "ENG-W", "credits": 8.0, "points": 20},
    {"name": "J Maguire", "role": "BOWL", "team": "IRE-W", "credits": 8.0, "points": 14},
    {"name": "K McCartney", "role": "BOWL", "team": "IRE-W", "credits": 8.0, "points": 14},
    {"name": "R Macdonald-Gay", "role": "BOWL", "team": "ENG-W", "credits": 8.0, "points": 0},
    {"name": "G Potts", "role": "BOWL", "team": "ENG-W", "credits": 7.0, "points": 0},
    {"name": "L McBride", "role": "BOWL", "team": "IRE-W", "credits": 6.5, "points": 0}
]

# ==========================================
# 2. NAMIBIA vs ZIMBABWE POOL
# ==========================================
NAM_ZIM_POOL = [
    {"name": "Z Green", "role": "WK", "team": "NAM", "credits": 6.0, "points": 125},
    {"name": "T Marumani", "role": "WK", "team": "ZIM", "credits": 7.5, "points": 118},
    {"name": "T Tsiga", "role": "WK", "team": "ZIM", "credits": 6.5, "points": 0},
    {"name": "B Curran", "role": "BAT", "team": "ZIM", "credits": 6.0, "points": 164},
    {"name": "A Volschenk", "role": "BAT", "team": "NAM", "credits": 8.0, "points": 139},
    {"name": "L Steenkamp", "role": "BAT", "team": "NAM", "credits": 7.5, "points": 89},
    {"name": "I Kaia", "role": "BAT", "team": "ZIM", "credits": 7.5, "points": 52},
    {"name": "D Myers", "role": "BAT", "team": "ZIM", "credits": 6.5, "points": 31},
    {"name": "M Kruger", "role": "BAT", "team": "NAM", "credits": 8.0, "points": 0},
    {"name": "J Taanyanda", "role": "BAT", "team": "NAM", "credits": 8.0, "points": 0},
    {"name": "van Lingen", "role": "BAT", "team": "NAM", "credits": 6.5, "points": 0},
    {"name": "D Leicher", "role": "BAT", "team": "NAM", "credits": 6.0, "points": 0},
    {"name": "B Evans", "role": "AR", "team": "ZIM", "credits": 7.5, "points": 315},
    {"name": "B Bennett", "role": "AR", "team": "ZIM", "credits": 7.5, "points": 238},
    {"name": "G Erasmus", "role": "AR", "team": "NAM", "credits": 8.0, "points": 204},
    {"name": "J Frylinck", "role": "AR", "team": "NAM", "credits": 7.0, "points": 182},
    {"name": "W Madhevere", "role": "AR", "team": "ZIM", "credits": 6.5, "points": 166},
    {"name": "S Raza", "role": "AR", "team": "ZIM", "credits": 9.0, "points": 165},
    {"name": "Smit", "role": "AR", "team": "NAM", "credits": 7.0, "points": 155},
    {"name": "Nicol Loftie-Eaton", "role": "AR", "team": "NAM", "credits": 6.5, "points": 48},
    {"name": "K Matigimu", "role": "AR", "team": "ZIM", "credits": 7.0, "points": 18},
    {"name": "J Balt", "role": "AR", "team": "NAM", "credits": 8.0, "points": 8},
    {"name": "G Cremer", "role": "AR", "team": "ZIM", "credits": 7.0, "points": 2},
    {"name": "R Trumpelmann", "role": "BOWL", "team": "NAM", "credits": 6.0, "points": 174},
    {"name": "N Nyamhuri", "role": "BOWL", "team": "ZIM", "credits": 8.0, "points": 130},
    {"name": "M Heingo", "role": "BOWL", "team": "NAM", "credits": 6.5, "points": 97},
    {"name": "B Muzarabani", "role": "BOWL", "team": "ZIM", "credits": 8.5, "points": 82},
    {"name": "J Brassell", "role": "BOWL", "team": "NAM", "credits": 7.0, "points": 68},
    {"name": "W Masakadza", "role": "BOWL", "team": "ZIM", "credits": 7.5, "points": 58},
    {"name": "B Scholtz", "role": "BOWL", "team": "NAM", "credits": 6.0, "points": 44},
    {"name": "W Smith", "role": "BOWL", "team": "NAM", "credits": 7.5, "points": 0},
    {"name": "B Shikongo", "role": "BOWL", "team": "NAM", "credits": 6.5, "points": 0}
]

# ==========================================
# 3. INDIA WOMEN vs HONG KONG WOMEN POOL
# ==========================================
IND_HK_POOL = [
    {"name": "Y Daswani", "role": "WK", "team": "HK-W", "credits": 7.0, "points": 58},
    {"name": "S Shahzad", "role": "WK", "team": "HK-W", "credits": 7.0, "points": 24},
    {"name": "J Kaur", "role": "WK", "team": "HK-W", "credits": 6.5, "points": 20},
    {"name": "R Ghosh", "role": "WK", "team": "IND-W", "credits": 8.0, "points": 18},
    {"name": "Kamalini", "role": "WK", "team": "IND-W", "credits": 7.0, "points": 0},
    {"name": "S Mandhana", "role": "BAT", "team": "IND-W", "credits": 8.5, "points": 65},
    {"name": "P Rawal", "role": "BAT", "team": "IND-W", "credits": 7.5, "points": 48},
    {"name": "B Fulmali", "role": "BAT", "team": "IND-W", "credits": 8.0, "points": 25},
    {"name": "H Kaur", "role": "BAT", "team": "IND-W", "credits": 8.0, "points": 9},
    {"name": "N Miles", "role": "BAT", "team": "HK-W", "credits": 6.5, "points": 0},
    {"name": "M Lamplough", "role": "AR", "team": "HK-W", "credits": 6.5, "points": 233},
    {"name": "S Verma", "role": "AR", "team": "IND-W", "credits": 9.0, "points": 140},
    {"name": "K Chan", "role": "AR", "team": "HK-W", "credits": 8.0, "points": 140},
    {"name": "D Sharma", "role": "AR", "team": "IND-W", "credits": 8.5, "points": 134},
    {"name": "M Bibi", "role": "AR", "team": "HK-W", "credits": 6.0, "points": 25},
    {"name": "M Hill", "role": "AR", "team": "HK-W", "credits": 8.0, "points": 2},
    {"name": "N Sharma", "role": "BOWL", "team": "IND-W", "credits": 6.5, "points": 126},
    {"name": "A Siu", "role": "BOWL", "team": "HK-W", "credits": 9.0, "points": 106},
    {"name": "S Charani", "role": "BOWL", "team": "IND-W", "credits": 8.0, "points": 95},
    {"name": "K Gaud", "role": "BOWL", "team": "IND-W", "credits": 6.5, "points": 82},
    {"name": "P Rawat", "role": "BOWL", "team": "IND-W", "credits": 8.0, "points": 47},
    {"name": "S Chan", "role": "BOWL", "team": "HK-W", "credits": 7.0, "points": 32},
    {"name": "R Venkatesh", "role": "BOWL", "team": "HK-W", "credits": 7.5, "points": 13},
    {"name": "C Chan", "role": "BOWL", "team": "HK-W", "credits": 6.5, "points": 4},
    {"name": "R Singh", "role": "BOWL", "team": "IND-W", "credits": 7.5, "points": 0},
    {"name": "R Yadav", "role": "BOWL", "team": "IND-W", "credits": 8.0, "points": 0},
    {"name": "I Sahar", "role": "BOWL", "team": "HK-W", "credits": 7.0, "points": 0},
    {"name": "A Reddy", "role": "BOWL", "team": "IND-W", "credits": 7.0, "points": 0},
    {"name": "H Wong", "role": "BOWL", "team": "HK-W", "credits": 6.5, "points": 0},
    {"name": "M Kaur", "role": "BOWL", "team": "HK-W", "credits": 6.0, "points": 0}
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS optimized_lineups (
            match_name TEXT,
            player_name TEXT,
            role TEXT,
            team TEXT,
            credits REAL,
            projected_points INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_lineup_to_db(match_name, selected_team):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for p in selected_team:
        cursor.execute("""
            INSERT INTO optimized_lineups (match_name, player_name, role, team, credits, projected_points)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (match_name, p["name"], p["role"], p["team"], p["credits"], p["points"]))
    conn.commit()
    conn.close()

def styled_optimize(match_name, pool, role_template):
    """Builds a team fulfilling exact positional requirements based on highest points."""
    # Organize players by role and sort by points descending
    categorized_pool = {"WK": [], "BAT": [], "AR": [], "BOWL": []}
    for player in pool:
        categorized_pool[player["role"]].append(player)
        
    for role in categorized_pool:
        categorized_pool[role] = sorted(categorized_pool[role], key=lambda x: x["points"], reverse=True)
        
    team = []
    total_credits = 0.0
    total_points = 0
    
    # Grab the top players for each required slot
    for role, required_count in role_template.items():
        selected = categorized_pool[role][:required_count]
        team.extend(selected)
        for p in selected:
            total_credits += p["credits"]
            total_points += p["points"]
            
    print(f"\n=======================================================")
    print(f"🏏 OPTIMIZED LINEUP: {match_name}")
    print(f"Template Enforced: {role_template}")
    print(f"=======================================================")
    
    if total_credits > 100.0:
        print(f"⚠️ WARNING: This exact template requires {total_credits} credits (Exceeds 100). Manual swaps needed.")
    else:
        print(f"✅ Total Credits Used: {total_credits}/100.0 | Total Past Points: {total_points}")
        
    print(f"\n{'PLAYER':<22} | {'TEAM':<6} | {'ROLE':<6} | {'CREDITS':<8} | {'POINTS'}")
    print("-" * 65)
    
    # Re-sort final printout by role structure for clean viewing
    for role in ["WK", "BAT", "AR", "BOWL"]:
        for p in [x for x in team if x["role"] == role]:
            print(f"{p['name']:<22} | {p['team']:<6} | {p['role']:<6} | {p['credits']:<8} | {p['points']}")
            
    log_lineup_to_db(match_name, team)

if __name__ == "__main__":
    init_db()
    
    # EXACT SL-W vs INA-W Match Blueprint
    bowling_heavy_style = {"WK": 1, "BAT": 2, "AR": 3, "BOWL": 5}
    
    styled_optimize("ENG-W vs IRE-W", ENG_IRE_POOL, bowling_heavy_style)
    styled_optimize("NAM vs ZIM", NAM_ZIM_POOL, bowling_heavy_style)
    styled_optimize("IND-W vs HK-W", IND_HK_POOL, bowling_heavy_style)
    
    print("\n💾 All 3 strictly formatted lineups have been processed and stored in SQLite!")
