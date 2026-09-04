# populate_vault.py - Apex Alpha OS: Universal ICC & Global Franchise Database Populator
import sqlite3
import os

def populate_global_vault():
    db_path = "global_cricket_vault.db"
    print(f"🔌 Connecting to Global Cricket Vault at: {os.path.abspath(db_path)}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ==========================================
    # 1. GLOBAL VENUES & METÉO MULTIPLIERS (30+)
    # ==========================================
    venues = [
        # --- India ---
        ("MA Chidambaram Stadium, Chennai", "India", "Spin-Friendly / Dry Surface", 1.30, "SPIN"),
        ("Wankhede Stadium, Mumbai", "India", "Batting Paradise / Pace Bounce", 1.20, "BAT"),
        ("Arun Jaitley Stadium, Delhi", "India", "Flat Track / Short Boundaries", 1.15, "BAT"),
        ("Eden Gardens, Kolkata", "India", "Balanced / True Bounce & Spin Assist", 1.20, "AR"),
        ("Narendra Modi Stadium, Ahmedabad", "India", "Large Outfield / Balanced Seam & Spin", 1.15, "AR"),
        ("M. Chinnaswamy Stadium, Bengaluru", "India", "High Altitude / Extreme Batting Paradise", 1.25, "BAT"),
        ("Rajiv Gandhi International Stadium, Hyderabad", "India", "Flat Batting Deck / High Scoring", 1.15, "BAT"),
        ("HPCA Stadium, Dharamshala", "India", "High Altitude / Seam & Swing", 1.35, "PACE"),
        
        # --- England ---
        ("Headingley Cricket Ground, Leeds", "England", "Overcast Seam & Swing", 1.35, "PACE"),
        ("Lord's Cricket Ground, London", "England", "Traditional Slope / Early Seam Movement", 1.30, "PACE"),
        ("The Oval, London", "England", "True Bounce / Batting Friendly & Reverse Swing", 1.20, "BAT"),
        ("Edgbaston, Birmingham", "England", "Aggressive Seam & Late Reverse", 1.25, "PACE"),
        ("Old Trafford, Manchester", "England", "Pace & Bounce with Late Spin", 1.20, "AR"),
        ("Trent Bridge, Nottingham", "England", "High-Scoring / Early Swing Assist", 1.20, "BAT"),
        
        # --- Australia ---
        ("Melbourne Cricket Ground (MCG), Melbourne", "Australia", "Balanced Track / Extra Bounce", 1.20, "AR"),
        ("Sydney Cricket Ground (SCG), Sydney", "Australia", "Turn & Spin Assist / Tactical Scoring", 1.25, "SPIN"),
        ("Adelaide Oval, Adelaide", "Australia", "Batting Friendly / Evening Seam Movement", 1.20, "BAT"),
        ("Optus Stadium, Perth", "Australia", "Extreme Pace & Steep Bounce", 1.35, "PACE"),
        ("The Gabba, Brisbane", "Australia", "Hard Deck / True Pace & Carry", 1.30, "PACE"),
        
        # --- West Indies ---
        ("Daren Sammy National Cricket Stadium, Saint Lucia", "West Indies", "Balanced Surface / Batting Friendly", 1.15, "BAT"),
        ("Kensington Oval, Bridgetown, Barbados", "West Indies", "True Pace & Bounce with Wind Assist", 1.25, "PACE"),
        ("Providence Stadium, Georgetown, Guyana", "West Indies", "Low & Slow / Heavy Spin Turning Track", 1.35, "SPIN"),
        ("Brian Lara Cricket Academy, Tarouba, Trinidad", "West Indies", "Variable Bounce / Mystery Spin Dominant", 1.30, "SPIN"),
        
        # --- South Africa ---
        ("Wanderers Stadium, Johannesburg", "South Africa", "High Altitude / High Pace & Bounce", 1.35, "PACE"),
        ("Newlands Cricket Ground, Cape Town", "South Africa", "Seam & Late Spin Assist", 1.25, "AR"),
        ("Kingsmead, Durban", "South Africa", "Coastal Moisture / Heavy Swing", 1.30, "PACE"),
        ("SuperSport Park, Centurion", "South Africa", "Steep Bounce & High Pace", 1.30, "PACE"),
        
        # --- UAE ---
        ("Dubai International Cricket Stadium, Dubai", "UAE", "Balanced Deck / Heavy Evening Dew", 1.20, "BAT"),
        ("Sharjah Cricket Stadium, Sharjah", "UAE", "Short Boundaries / Extreme Batting Paradise", 1.25, "BAT"),
        ("Sheikh Zayed Cricket Stadium, Abu Dhabi", "UAE", "Large Boundaries / Pace & Spin Control", 1.20, "AR"),
        
        # --- Sri Lanka, Pakistan & USA ---
        ("R. Premadasa Stadium, Colombo", "Sri Lanka", "Slow Turner / Spin Dominant", 1.35, "SPIN"),
        ("Pallekele International Stadium, Kandy", "Sri Lanka", "Early Seam / Middle Overs Spin", 1.25, "AR"),
        ("Gaddafi Stadium, Lahore", "Pakistan", "Flat Batting Paradise / Death Reverse Swing", 1.20, "BAT"),
        ("National Bank Stadium, Karachi", "Pakistan", "Dry Deck / Variable Reverse & Spin", 1.25, "AR"),
        ("Grand Prairie Stadium, Dallas", "USA", "Hard Pitch / High Scoring T20 Track", 1.20, "BAT"),
        ("Central Broward Regional Park, Florida", "USA", "True Bounce / High-Scoring Short Boundaries", 1.20, "BAT")
    ]

    cursor.executemany('''
        INSERT OR REPLACE INTO Global_Venues (Venue_Name, Country, Pitch_Profile, Meteo_Multiplier, Favored_Role)
        VALUES (?, ?, ?, ?, ?)
    ''', venues)
    print(f"✅ Injected {len(venues)} Global Venues across 9 cricket nations.")

    # =========================================================================
    # 2. GLOBAL PLAYERS: ICC (TEST/ODI/T20) & FRANCHISE LEAGUES (IPL/BBL/CPL...)
    # =========================================================================
    players = [
        # --- ICC International & Test Pools ---
        ("Virat Kohli", "India", "Royal Challengers Bengaluru", "BAT", 10.0),
        ("Rohit Sharma", "India", "Mumbai Indians", "BAT", 9.5),
        ("Jasprit Bumrah", "India", "Mumbai Indians", "PACE", 9.5),
        ("Suryakumar Yadav", "India", "Mumbai Indians", "BAT", 9.5),
        ("Hardik Pandya", "India", "Mumbai Indians", "AR", 9.5),
        ("Ravindra Jadeja", "India", "Chennai Super Kings", "AR", 9.0),
        ("Rishabh Pant", "India", "Delhi Capitals", "WK", 9.0),
        ("Shubman Gill", "India", "Gujarat Titans", "BAT", 9.0),
        ("Yashasvi Jaiswal", "India", "Rajasthan Royals", "BAT", 9.0),
        ("Mohammed Siraj", "India", "Gujarat Titans", "PACE", 8.5),
        ("Kuldeep Yadav", "India", "Delhi Capitals", "SPIN", 8.5),
        ("Arshdeep Singh", "India", "Punjab Kings", "PACE", 8.5),
        ("Axar Patel", "India", "Delhi Capitals", "AR", 8.5),

        # --- Australia ---
        ("Travis Head", "Australia", "Sunrisers Hyderabad", "BAT", 9.5),
        ("Pat Cummins", "Australia", "Sunrisers Hyderabad", "PACE", 9.5),
        ("Mitchell Starc", "Australia", "Kolkata Knight Riders", "PACE", 9.0),
        ("Glenn Maxwell", "Australia", "Melbourne Stars", "AR", 9.0),
        ("Josh Hazlewood", "Australia", "Royal Challengers Bengaluru", "PACE", 9.0),
        ("Steve Smith", "Australia", "Sydney Sixers", "BAT", 9.0),
        ("Marnus Labuschagne", "Australia", "Brisbane Heat", "BAT", 8.5),
        ("Marcus Stoinis", "Australia", "Lucknow Super Giants", "AR", 8.5),
        ("Adam Zampa", "Australia", "Melbourne Renegades", "SPIN", 8.5),
        ("Cameron Green", "Australia", "Royal Challengers Bengaluru", "AR", 8.5),
        ("Josh Inglis", "Australia", "Perth Scorchers", "WK", 8.5),
        ("Tim David", "Australia", "Mumbai Indians", "BAT", 8.0),

        # --- England ---
        ("Joe Root", "England", "Trent Rockets", "BAT", 9.5),
        ("Harry Brook", "England", "Northern Superchargers", "BAT", 9.0),
        ("Jos Buttler", "England", "Rajasthan Royals", "WK", 9.5),
        ("Jofra Archer", "England", "Southern Brave", "PACE", 9.0),
        ("Ben Stokes", "England", "Northern Superchargers", "AR", 9.5),
        ("Phil Salt", "England", "Kolkata Knight Riders", "WK", 9.0),
        ("Liam Livingstone", "England", "Birmingham Phoenix", "AR", 8.5),
        ("Sam Curran", "England", "Oval Invincibles", "AR", 8.5),
        ("Gus Atkinson", "England", "Oval Invincibles", "PACE", 8.5),
        ("Adil Rashid", "England", "Northern Superchargers", "SPIN", 8.5),
        ("Ben Duckett", "England", "Birmingham Phoenix", "BAT", 8.5),
        ("Jamie Smith", "England", "Oval Invincibles", "WK", 8.5),
        ("Shoaib Bashir", "England", "England Test", "SPIN", 8.0),

        # --- Pakistan ---
        ("Babar Azam", "Pakistan", "Peshawar Zalmi", "BAT", 9.5),
        ("Mohammad Rizwan", "Pakistan", "Multan Sultans", "WK", 9.0),
        ("Shaheen Afridi", "Pakistan", "Lahore Qalandars", "PACE", 9.0),
        ("Naseem Shah", "Pakistan", "Islamabad United", "PACE", 8.5),
        ("Haris Rauf", "Pakistan", "Lahore Qalandars", "PACE", 8.5),
        ("Shadab Khan", "Pakistan", "Islamabad United", "AR", 8.5),
        ("Fakhar Zaman", "Pakistan", "Lahore Qalandars", "BAT", 8.5),
        ("Salman Ali Agha", "Pakistan", "Islamabad United", "AR", 8.5),
        ("Aamer Jamal", "Pakistan", "Peshawar Zalmi", "AR", 8.0),
        ("Saud Shakeel", "Pakistan", "Quetta Gladiators", "BAT", 8.0),
        ("Sajid Khan", "Pakistan", "Pakistan Test", "SPIN", 8.0),

        # --- South Africa ---
        ("Heinrich Klaasen", "South Africa", "Sunrisers Hyderabad", "WK", 9.5),
        ("Kagiso Rabada", "South Africa", "MI Cape Town", "PACE", 9.0),
        ("Quinton de Kock", "South Africa", "Durban's Super Giants", "WK", 9.0),
        ("Aiden Markram", "South Africa", "Sunrisers Eastern Cape", "AR", 9.0),
        ("David Miller", "South Africa", "Paarl Royals", "BAT", 8.5),
        ("Marco Jansen", "South Africa", "Sunrisers Eastern Cape", "AR", 8.5),
        ("Anrich Nortje", "South Africa", "Pretoria Capitals", "PACE", 8.5),
        ("Keshav Maharaj", "South Africa", "Durban's Super Giants", "SPIN", 8.5),
        ("Tristan Stubbs", "South Africa", "Sunrisers Eastern Cape", "BAT", 8.5),
        ("Tabraiz Shamsi", "South Africa", "Paarl Royals", "SPIN", 8.0),

        # --- West Indies & CPL ---
        ("Nicholas Pooran", "West Indies", "Trinbago Knight Riders", "WK", 9.5),
        ("Andre Russell", "West Indies", "Trinbago Knight Riders", "AR", 9.5),
        ("Sunil Narine", "West Indies", "Trinbago Knight Riders", "SPIN", 9.0),
        ("Roston Chase", "West Indies", "Saint Lucia Kings", "AR", 9.0),
        ("Tim Seifert", "New Zealand", "Saint Lucia Kings", "WK", 9.0),
        ("Shai Hope", "West Indies", "Guyana Amazon Warriors", "WK", 9.5),
        ("Shimron Hetmyer", "West Indies", "Guyana Amazon Warriors", "BAT", 9.5),
        ("Romario Shepherd", "West Indies", "Guyana Amazon Warriors", "AR", 9.0),
        ("Matthew Forde", "West Indies", "Saint Lucia Kings", "PACE", 8.5),
        ("Maheesh Theekshana", "Sri Lanka", "Saint Lucia Kings", "SPIN", 9.0),
        ("Noor Ahmad", "Afghanistan", "Saint Lucia Kings", "SPIN", 8.5),
        ("Dwaine Pretorius", "South Africa", "Guyana Amazon Warriors", "AR", 8.5),
        ("Imran Tahir", "South Africa", "Guyana Amazon Warriors", "SPIN", 8.5),
        ("Shamar Joseph", "West Indies", "Guyana Amazon Warriors", "PACE", 8.5),
        ("Khary Pierre", "West Indies", "Guyana Amazon Warriors", "SPIN", 8.0),
        ("Ackeem Auguste", "West Indies", "Saint Lucia Kings", "BAT", 8.0),
        ("Shadley van Schalkwyk", "USA", "Saint Lucia Kings", "PACE", 8.0),
        ("Jason Holder", "West Indies", "Barbados Royals", "AR", 9.0),
        ("Rovman Powell", "West Indies", "Barbados Royals", "BAT", 8.5),
        ("Kieron Pollard", "West Indies", "Trinbago Knight Riders", "AR", 8.5),

        # --- Afghanistan & Sri Lanka & Bangladesh ---
        ("Rashid Khan", "Afghanistan", "Gujarat Titans", "SPIN", 9.5),
        ("Rahmanullah Gurbaz", "Afghanistan", "Kolkata Knight Riders", "WK", 8.5),
        ("Mohammad Nabi", "Afghanistan", "Guyana Amazon Warriors", "AR", 8.5),
        ("Fazalhaq Farooqi", "Afghanistan", "Sunrisers Hyderabad", "PACE", 8.5),
        ("Wanindu Hasaranga", "Sri Lanka", "Sunrisers Hyderabad", "SPIN", 9.0),
        ("Matheesha Pathirana", "Sri Lanka", "Chennai Super Kings", "PACE", 9.0),
        ("Charith Asalanka", "Sri Lanka", "Saint Lucia Kings", "BAT", 8.5),
        ("Kusal Mendis", "Sri Lanka", "Lanka Premier League", "WK", 8.5),
        ("Shakib Al Hasan", "Bangladesh", "Bangladesh Premier League", "AR", 9.0),
        ("Mustafizur Rahman", "Bangladesh", "Chennai Super Kings", "PACE", 8.5),
        ("Taskin Ahmed", "Bangladesh", "Bangladesh Premier League", "PACE", 8.0),
        ("Litton Das", "Bangladesh", "Bangladesh Premier League", "WK", 8.0),

        # --- Domestic Leagues: TNPL & DPL ---
        ("Varun Chakaravarthy", "India", "Dindigul Dragons", "SPIN", 9.5),
        ("Baba Indrajith", "India", "Dindigul Dragons", "WK", 9.0),
        ("Shivam Singh", "India", "Dindigul Dragons", "BAT", 9.0),
        ("Sandeep Warrier", "India", "Dindigul Dragons", "PACE", 8.5),
        ("Sanjay Yadav", "India", "Trichy Grand Cholas", "AR", 9.0),
        ("Suresh Kumar", "India", "Trichy Grand Cholas", "WK", 9.0),
        ("V Athisayaraj Davidson", "India", "Trichy Grand Cholas", "PACE", 8.5),
        ("N Jagadeesan", "India", "Chepauk Super Gillies", "WK", 9.5),
        ("Shahrukh Khan", "India", "Lyca Kovai Kings", "BAT", 9.5),
        ("M Siddharth", "India", "Lyca Kovai Kings", "SPIN", 9.0),
        ("Ayush Badoni", "India", "South Delhi Superstarz", "BAT", 9.5),
        ("Sarthak Ranjan", "India", "North Delhi Strikers", "BAT", 9.5),
        ("Mayank Dagar", "India", "North Delhi Strikers", "SPIN", 9.0),
        ("Harshit Rana", "India", "North Delhi Strikers", "PACE", 9.0)
    ]

    cursor.executemany('''
        INSERT OR REPLACE INTO Global_Players (Player_Name, National_Team, Franchise_Team, Role, Base_Credits)
        VALUES (?, ?, ?, ?, ?)
    ''', players)
    print(f"✅ Injected {len(players)} Global Players across ICC and worldwide leagues.")

    # Commit all changes
    conn.commit()
    conn.close()
    print("🚀 Global Cricket Vault is fully armed and ready for the Quantitative Optimizer Engine!")

if __name__ == "__main__":
    populate_global_vault()
