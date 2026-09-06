import os
import subprocess

def run_command(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Pipeline step failed: {command}")

if __name__ == "__main__":
    print("==========================================")
    print("  PROD PIPELINE: CRICSHEET + PITCH + METEO  ")
    print("==========================================")
    
    # 1. Clean legacy mock files
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
    
    print("==========================================")
    print(" Full Cricsheet + Pitch + Meteo Pipeline Complete!")
    print("==========================================")
