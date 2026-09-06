#!/bin/sh
echo "=========================================="
echo "  CLOUD DFS BATCH PROCESSOR STARTING"
echo "=========================================="

echo "[1/5] Fetching live API projections..."
python fetch_live_api.py

echo "[2/5] Applying Vegas sports market adjustments..."
python vegas_odds_integrator.py

echo "[3/5] Pulling real-time weather data..."
python meteo_integrator.py

echo "[4/5] Generating 20-team GPP portfolio..."
python gpp_multi_generator.py

echo "[5/5] Generating interactive HTML risk dashboard..."
python generate_report.py

echo "=========================================="
echo "  PIPELINE COMPLETE."
echo "=========================================="
