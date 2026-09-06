import os
import subprocess

def run_command(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Pipeline step failed: {command}")

def upload_to_gcs():
    bucket_name = os.environ.get("GCP_DFS_BUCKET")
    if not bucket_name:
        print("🖥️ Local run detected (No GCP_DFS_BUCKET variable set). Skipping cloud upload.")
        return

    print(f"☁️ Cloud environment detected. Initiating GCP Storage upload to bucket: {bucket_name}...")
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        files_to_upload = ["fully_compounded_gpp_portfolio.csv", "portfolio_report.html"]
        for file_name in files_to_upload:
            if os.path.exists(file_name):
                blob = bucket.blob(file_name)
                blob.upload_from_filename(file_name)
                print(f"✅ Success! {file_name} securely uploaded to GCP Bucket: {bucket_name}")
            else:
                print(f"⚠️ Warning: {file_name} not found for cloud upload.")
    except Exception as e:
        print(f"❌ GCP Upload Failed: {e}")

if __name__ == "__main__":
    print("==========================================")
    print("  PROD PIPELINE: CRICSHEET + PITCH + METEO  ")
    print("==========================================")
    
    # 1. Clean legacy mock files if any
    for f in ["live_slate.csv", "vegas_adjusted_slate.csv", "weather_and_vegas_adjusted_slate.csv"]:
        if os.path.exists(f):
            os.remove(f)
            
    # 2. Historical Data Ingestion
    run_command("python parse_cricsheet_csv.py")
    
    # 3. Base Feature Engineering
    run_command("python pipeline_features.py")
    
    # 4. Global Pitch & Venue Profiling
    run_command("python pipeline_venue_profiler.py")
    
    # 5. Open-Meteo Meteorological Injector
    run_command("python pipeline_weather_injector.py")
    
    # 6. Betting Market Odds & Final Projections
    run_command("python pipeline_market_engine.py")
    
    # 7. Production MILP Optimizer Portfolio Generation
    run_command("python pipeline_optimizer_production.py")
    
    # 8. Cloud Synchronization
    upload_to_gcs()
    
    print("==========================================")
    print(" Full Cricsheet + Pitch + Meteo Pipeline Complete!")
    print("==========================================")
