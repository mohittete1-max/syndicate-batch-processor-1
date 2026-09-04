import os
import json

def load_all_squads_to_engine():
    """Compiles and saves all official team squads into a central engine configuration file."""
        
    master_squads = {
        "Namibia": [
            "Malan Kruger", "Junior Taanyanda", "Gerhard Erasmus", "Jan Frylinck", 
            "Louren Steenkamp", "Alexander Volschenk", "Zane Green", "JJ Smit", 
            "Michael van Lingen", "Bernard Scholtz", "Ruben Trumpelmann", "Jack Brassell", 
            "Max Heingo", "Waldo Smith", "Jan Balt", "Jan Nicol Loftie-Eaton"
        ],
        "South Africa": [
            "Tony de Zorzi", "Lhuan-dre Pretorius", "Rubin Hermann", "Jordan Hermann", 
            "Dewald Brevis", "Jason Smith", "Prenelan Subrayen", "Bjorn Fortuin", 
            "Duan Jansen", "Lutho Sipamla", "Kwena Maphaka", "Nqabayomzi Peter", 
            "Eathan Bosch", "Connor Esterhuizen", "Nqobani Mokoena"
        ],
        "Thailand Women": [
            "Phannita Maya", "Aphisara Suwanchonrathi", "Nannapat Koncharoenkai", "Naruemol Chaiwai", 
            "Chanida Sutthiruang", "Nannaphat Chaihan", "Chayanisa Phengpaen", "Onnicha Kamchomphu", 
            "Suleeporn Laomi", "Sunida Chaturongrattana", "Thipatcha Putthawong", "Nattakan Chantam", 
            "Koranit Suwanchonrathi", "Thanrada Seesawan", "Naomi Hamilton"
        ],
        "Hong Kong, China Women": [
            "Natasha Miles", "Mariko Hill", "Yasmin Daswani", "Maryam Bibi", 
            "Kary Chan", "Marina Lamplough", "Alison Siu", "Iqra Sahar", 
            "Joyleen Kaur", "Shanzeen Shahzad", "Ruchitha Venkatesh", "Charlotte Chan", 
            "Shing Chan Dorothea", "Kaur Mahekdeep", "Hailey Wong"
        ],
        "Scotland Women": [
            "Sarah Bryce", "Darcey Carter", "Katherine Fraser", "Megan McColl", 
            "Maryam Faisal", "Niamh Robertson Jack", "Nayma Sheikh", "Isabella Watson", 
            "Charlotte Nevard", "Abtaha Maqsood", "Maisie Maceira", "Gabriella Fontenla", 
            "Pippa Sproul", "Rebecca McCrossan", "Ellen Watson"
        ],
        "Netherlands Women": [
            "Babette de Leede", "Sanya Khurana", "Phebe Molkenboer", "Noa Mais", 
            "Merel Dekeling", "Frederique Overdijk", "Robine Rijke", "Myrthe van den Raad", 
            "Silver Siegers", "Hannah Landheer", "Caroline de Lange", "Lara Leemhuis", 
            "Rosalie Lawrence"
        ],
        "Edinburgh Castle Rockers": [
            "Ross Adair", "Andries Gous", "Gareth Delany", "Brandon McMullen", 
            "Laurie Evans", "JJ Smuts", "Tom Curran", "Mitchell Santner", 
            "Andrew Tye", "Trent Boult", "Safyaan Sharif", "Mark Watt", 
            "Finlay McCreath", "Sean Solia", "Jack Jarvis", "Rushil Ugarkar", "Ollie Jones"
        ],
        "Amsterdam Flames": [
            "Max O'Dowd", "Yuvraj Samra", "Bas de Leede", "Curtis Campher", 
            "Tim David", "Scott Edwards", "Michael Bracewell", "Tim Pringle", 
            "Kyle Klein", "David Payne", "Richard Gleeson", "Aryan Dutt", 
            "Ali Hasan", "Jordan Neill", "David Rushmere", "Steven Smith", "Ajinkya Rahane"
        ]
    }
    
    output_path = r"C:\Users\User\OneDrive\Desktop\Cricket\master_squad_database.json"
    with open(output_path, "w") as f:
        json.dump(master_squads, f, indent=4)
        
    print(f"[SUCCESS] All official squads successfully loaded and mapped to engine database -> {output_path}")

if __name__ == "__main__":
    load_all_squads_to_engine()
