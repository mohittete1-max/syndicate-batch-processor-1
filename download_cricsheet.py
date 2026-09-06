import os
import zipfile
import urllib.request

def download_cricsheet_archive(target_dir="C:/Users/User/OneDrive/Desktop/Cricket/json_data"):
    os.makedirs(target_dir, exist_ok=True)
    url = "https://cricsheet.org/downloads/all_json.zip"
    zip_path = os.path.join(target_dir, "all_json.zip")
    
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]
    urllib.request.install_opener(opener)
    
    print("Downloading the complete Cricsheet JSON archive...")
    urllib.request.urlretrieve(url, zip_path)
    
    if zipfile.is_zipfile(zip_path):
        print("Extracting match files into json_data...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        print("Extraction complete. All formats and competitions are now ready.")
    else:
        print("Error: Downloaded file is not a valid zip archive.")
        
    if os.path.exists(zip_path):
        os.remove(zip_path)

if __name__ == "__main__":
    download_cricsheet_archive()

    
