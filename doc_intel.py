import re
import pandas as pd

def parse_squad_document(file_path):
    """
    Parses unstructured text or exported text files containing match squads,
    credits, and roles for the Apex Alpha OS optimizer.
    """
    structured_data = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            
        for line in lines:
            # Example pattern matching: "Player Name | Role | Team | Credits | Base Pts"
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                structured_data.append({
                    "name": parts[0],
                    "role": parts[1].upper(),
                    "team": parts[2],
                    "credits": float(parts[3]),
                    "base_pts": float(parts[4])
                })
                
        if structured_data:
            print(f"✅ Document Intelligence: Successfully extracted {len(structured_data)} player records.")
            return pd.DataFrame(structured_data)
        else:
            print("⚠️ Document Intelligence: No matching records found in the file structure.")
            return None
            
    except Exception as e:
        print(f"⚠️ Parsing Error: {e}")
        return None
