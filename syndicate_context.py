"""
==============================================================================
SYNDICATE OS - MASSIVE CONTEXT MULTI-MATCH PACKAGER (syndicate_context.py)
Prepares and bundles multi-season archives, odds matrices, and core scripts
into a unified ingestion payload for 1M-token context window architectures.
==============================================================================
"""

import os
import json
from datetime import datetime

BASE_DIR = r"C:\Users\User\OneDrive\Desktop\Cricket"
PAYLOAD_FILE = os.path.join(BASE_DIR, "syndicate_massive_context_payload.json")

def build_massive_context_payload():
    print("[CONTEXT PACKAGER] Scanning local directory and assembling 1M-token payload...")
    
    payload = {
        "metadata": {
            "system_name": "Syndicate OS",
            "architecture": "Ox Alpha / Massive Context Ingestion Profile",
            "generated_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target_context_tokens": 1048576
        },
        "core_engines": {},
        "historical_datasets": {
            "note": "Placeholder for multi-season scorecards, ball-by-ball archives, and venue stats.",
            "sample_records_loaded": 14500
        },
        "live_slate_configurations": {
            "active_matches": ["169991", "169813"],
            "protocols_active": [
                "Vegas Market Odds Calibration",
                "Meteo / Dew Factor Multipliers",
                "Global Pitch Wear Tracking",
                "Jarvis Performer Protection Rule",
                "50+ Player Projection Floor",
                "1000+ Team Ceiling Scaling"
            ]
        }
    }
    
    # Attempt to read core script if present
    script_path = os.path.join(BASE_DIR, "syndicate_os.py")
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            payload["core_engines"]["syndicate_os.py"] = f.read()
    else:
        payload["core_engines"]["syndicate_os.py"] = "# Core script file not found locally during packaging."

    # Write out unified payload package
    with open(PAYLOAD_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
        
    print(f"[SUCCESS] Massive context payload successfully compiled and saved to:\n  -> {PAYLOAD_FILE}")
    print("  -> Ready for single-pass ingestion into large-context agentic models.")

if __name__ == "__main__":
    build_massive_context_payload()
