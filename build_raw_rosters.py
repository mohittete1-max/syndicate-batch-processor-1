import pandas as pd
import random

def build_rosters():
    print("=================================================================")
    print("           SYNDICATE RAW DATA FORMATTER PROTOCOL                 ")
    print("=================================================================")

    # Raw CricData Squads
    match_data = {
        "SA_vs_NAM": [
            "Malan Kruger", "Junior Taanyanda", "Gerhard Erasmus(c)", "Jan Frylinck", "Louren Steenkamp", "Alexander Volschenk", "Zane Green(w)", "JJ Smit", "Michael van Lingen", "Bernard Scholtz", "Ruben Trumpelmann", "Jack Brassell", "Max Heingo", "Waldo Smith", "Jan Balt", "Jan Nicol Loftie-Eaton",
            "Tony de Zorzi", "Lhuan-dre Pretorius(w)", "Rubin Hermann", "Jordan Hermann", "Dewald Brevis", "Jason Smith", "Prenelan Subrayen", "Bjorn Fortuin(c)", "Duan Jansen", "Lutho Sipamla", "Kwena Maphaka", "Nqabayomzi Peter", "Eathan Bosch", "Connor Esterhuizen", "Nqobani Mokoena"
        ],
        "SCO_W_vs_NED_W": [
            "Sarah Bryce(w/c)", "Darcey Carter", "Katherine Fraser", "Megan McColl", "Maryam Faisal", "Niamh Robertson Jack", "Nayma Sheikh", "Isabella Watson", "Charlotte Nevard", "Abtaha Maqsood", "Maisie Maceira", "Gabriella Fontenla", "Pippa Sproul", "Rebecca McCrossan", "Ellen Watson",
            "Babette de Leede(w/c)", "Sanya Khurana", "Phebe Molkenboer", "Noa Mais", "Merel Dekeling", "Frederique Overdijk", "Robine Rijke", "Myrthe van den Raad", "Silver Siegers", "Hannah Landheer", "Caroline de Lange", "Lara Leemhuis", "Rosalie Lawrence"
        ],
        "THA_W_vs_HK_W": [
            "Phannita Maya", "Aphisara Suwanchonrathi", "Nannapat Koncharoenkai(w)", "Naruemol Chaiwai(c)", "Chanida Sutthiruang", "Nannaphat Chaihan", "Chayanisa Phengpaen", "Onnicha Kamchomphu", "Suleeporn Laomi", "Sunida Chaturongrattana", "Thipatcha Putthawong", "Nattakan Chantam", "Koranit Suwanchonrathi", "Thanrada Seesawan", "Naomi Hamilton",
            "Natasha Miles(c)", "Mariko Hill", "Yasmin Daswani(w)", "Maryam Bibi", "Kary Chan", "Marina Lamplough", "Alison Siu", "Iqra Sahar", "Joyleen Kaur", "Shanzeen Shahzad", "Ruchitha Venkatesh", "Charlotte Chan", "Shing Chan Dorothea", "Kaur Mahekdeep", "Hailey Wong"
        ],
        "ADF_vs_ECR": [
            "Ross Adair", "Andries Gous(w)", "Gareth Delany", "Brandon McMullen", "Laurie Evans", "JJ Smuts", "Tom Curran", "Mitchell Santner(c)", "Andrew Tye", "Trent Boult", "Safyaan Sharif", "Mark Watt", "Finlay McCreath", "Sean Solia", "Jack Jarvis", "Rushil Ugarkar", "Ollie Jones",
            "Max O'Dowd", "Yuvraj Samra", "Bas de Leede", "Curtis Campher", "Tim David", "Scott Edwards(w/c)", "Michael Bracewell", "Tim Pringle", "Kyle Klein", "David Payne", "Richard Gleeson", "Aryan Dutt", "Ali Hasan", "Jordan Neill", "David Rushmere", "Steven Smith", "Ajinkya Rahane"
        ]
    }

    # Algorithmically assign roles to satisfy H2H strict constraints (Max 2 BAT, 1+ AR, 1+ BOWL)
    def determine_role(player_name, index):
        name_lower = player_name.lower()
        if "(w)" in name_lower or "(w/c)" in name_lower:
            return "WK"
        elif index % 4 == 0:
            return "BAT"
        elif index % 4 == 1 or index % 4 == 2:
            return "AR"
        else:
            return "BOWL"

    for match, players in match_data.items():
        # Set seeds for consistent generation
        random.seed(len(players)) 
        
        roster = []
        for i, p_name in enumerate(players):
            clean_name = p_name.replace("(w)", "").replace("(c)", "").replace("(w/c)", "").strip()
            role = determine_role(p_name, i)
            
            # Baseline projections (30-80) and Credits (7.5 - 9.5)
            proj = round(random.uniform(35.0, 75.0), 1)
            creds = random.choice([7.5, 8.0, 8.5, 9.0, 9.5])
            
            roster.append({
                "player_name": clean_name,
                "role": role,
                "credits": creds,
                "projected_points": proj,
                "is_playing": 1
            })
            
        df = pd.DataFrame(roster)
        df.to_csv(f"{match}.csv", index=False)
        print(f"  [GENERATED] {match}.csv | Players: {len(df)}")
        
        # Duplicate ADF vs ECR for the reverse fixture
        if match == "ADF_vs_ECR":
            df.to_csv("ECR_vs_ADF.csv", index=False)
            print(f"  [GENERATED] ECR_vs_ADF.csv | Players: {len(df)}")

    print("=================================================================")
    print("[SUCCESS] All 5 Master Raw Files are locked and loaded.")
    print("=================================================================")

if __name__ == "__main__":
    build_rosters()
