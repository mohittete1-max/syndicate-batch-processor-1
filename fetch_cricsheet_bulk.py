import requests
import zipfile
import io
from pathlib import Path

def update_cricsheet_data(dataset: str = "t20s", dest_folder: str = "data/raw"):
    """
    Downloads and extracts a bulk JSON dataset from Cricsheet.
    Common dataset options: 'all', 't20s', 'odis', 'tests', 'ipl', 'bbl'
    """
    url = f"https://cricsheet.org/downloads/{dataset}_json.zip"
    
    # Ensure the destination folder exists (and ignore if it already does)
    extract_path = Path(dest_folder)
    extract_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Fetching {dataset.upper()} dataset from {url}...")
    
    try:
        # Request the zip file
        response = requests.get(url, timeout=30)
        response.raise_for_status() 
        
        print(f"Download complete. Extracting files to {extract_path}...")
        
        # Read the zip file from memory and extract
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Filter to just JSON files (Cricsheet includes a README.txt)
            file_list = z.namelist()
            json_files = [f for f in file_list if f.endswith('.json')]
            
            # Extract files, overwriting any existing ones with the same name
            for file in json_files:
                z.extract(file, extract_path)
            
        print(f"Success! Updated {len(json_files)} match files in '{extract_path}'.")
        
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred while downloading: {e}")
    except zipfile.BadZipFile:
        print("Error: The downloaded data was not a valid zip archive.")

if __name__ == "__main__":
    # Example: Grab IPL and general T20 data for standard modeling
    update_cricsheet_data("ipl", dest_folder="data/raw/ipl")
    update_cricsheet_data("t20s", dest_folder="data/raw/t20s")
