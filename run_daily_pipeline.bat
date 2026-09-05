@echo off
echo ==========================================
echo   SYNDICATE DFS BATCH PROCESSOR STARTING
echo ==========================================
echo.

:: 1. Activate the base Anaconda environment
call "C:\Users\User\anaconda3\Scripts\activate.bat" base

:: 2. Navigate to the project folder
cd /d "C:\Users\User\OneDrive\Desktop\Cricket"

:: 3. Run the pipeline in exact sequence
echo [1/4] Fetching live API projections...
python fetch_live_api.py
if %ERRORLEVEL% NEQ 0 goto :error

echo [2/4] Pulling real-time weather data...
python meteo_integrator.py
if %ERRORLEVEL% NEQ 0 goto :error

echo [3/4] Applying Vegas sports market adjustments...
python vegas_odds_integrator.py
if %ERRORLEVEL% NEQ 0 goto :error

echo [4/4] Generating 20-team GPP portfolio...
python gpp_multi_generator.py
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo ==========================================
echo   PIPELINE COMPLETE. PORTFOLIO EXPORTED.
echo ==========================================
goto :end

:error
echo.
echo [!] CRITICAL ERROR: Pipeline failed. Check logs.
pause

:end
