# live_monitor.py
import time
import scraper
import universal_cricket_optimizer as optimizer # Importing your function

def monitor_live_match(target_url):
    print(f"Monitoring live match feed: {target_url}")
    last_score = 0
    
    while True:
        try:
            live_df = scraper.fetch_live_stats(target_url)
            current_score = live_df['Points'].sum()
            
            # Trigger Logic (if points shifted significantly)
            if abs(current_score - last_score) > 50:
                print(f"--- SIGNIFICANT UPDATE DETECTED: {current_score} pts ---")
                print("Triggering auto-reoptimization...")
                
                # Now this works!
                optimizer.run_optimization_engine() 
                
                print("Portfolio refreshed.")
                last_score = current_score
            
            time.sleep(10) # 10 seconds for testing
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_live_match("https://www.example.com/live-scorecard")
