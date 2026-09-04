import os
import requests
import zipfile
import io
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_and_extract_cricsheet(base_url="https://cricsheet.org/matches/", dest_folder="data/raw/all_matches"):
    """
    Scrapes the Cricsheet webpage to find and download the bulk JSON dataset.
    """
    print(f"Scraping {base_url} for download links...")
    
    try:
        # Fetch the HTML content of the page
        response = requests.get(base_url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the webpage: {e}")
        return

    # Parse the HTML to find the download links
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all anchor tags (<a>) where the hyperlink text is exactly 'JSON'
    json_links = soup.find_all('a', string=lambda text: text and 'JSON' in text)
    
    if not json_links:
        print("No JSON download links found on the page.")
        return
        
    print(f"Found {len(json_links)} JSON download links on the page.")
    
    # The first link under "THE DATA" corresponds to "All matches"
    # We only need this one to get the entire database without duplicates
    all_matches_link = json_links[0]
    href = all_matches_link.get('href')
    full_url = urljoin(base_url, href)
    
    print(f"\nTargeting 'All matches' dataset: {full_url}")
    
    os.makedirs(dest_folder, exist_ok=True)
    
    try:
        print("Downloading zip archive into memory (this may take a minute)...")
        zip_resp = requests.get(full_url, timeout=60)
        zip_resp.raise_for_status()
        
        print("Download complete. Extracting JSON files...")
        with zipfile.ZipFile(io.BytesIO(zip_resp.content)) as z:
            # Filter for .json files to avoid extracting READMEs
            json_files = [f for f in z.namelist() if f.endswith('.json')]
            
            for file in json_files:
                z.extract(file, dest_folder)
            
        print(f"Success! Extracted {len(json_files)} match files to '{dest_folder}'.")
        
    except Exception as e:
        print(f"Failed to download or extract the dataset: {e}")

if __name__ == "__main__":
    # Run the scraper and dump everything into the raw data folder
    scrape_and_extract_cricsheet()
