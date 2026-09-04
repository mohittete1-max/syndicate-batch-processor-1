# Syndicate Batch Processor

A Python-based Integer Linear Programming (ILP) engine built for advanced fantasy cricket optimization, lineup simulation, and leverage analysis.

## Core Features
- **ILP Optimization**: Utilizes `pulp` to solve team selection constraints under salary caps, role limits, and ownership ceilings (`pOWN%`).
- **Environmental & Pitch Adjustments**: Automatically fetches live weather data via Open-Meteo and applies venue-specific multipliers.
- **Match Context & Blowout Detection**: Automatically categorizes match tiers and adjusts simulation noise or favorite-team locking.
- **Interactive Visualizations**: Generates dynamic HTML leverage scatter plots using `plotly`.

## Tech Stack
- Python 3.x
- PuLP, Pandas, NumPy, Plotly, Requests
