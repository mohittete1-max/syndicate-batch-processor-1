# Syndicate OS - Power BI & DAX Playbook

## Core Measures

### 1. Projection Error
Projection Error = [Actual_Points] - [Projected_Points]

### 2. Leverage Score (GPP Value)
Leverage_Gain = [Actual_Points] * (100 - [base_pOWN]) / 100

### 3. Final Lineup Total Points
Total_Score = 
CALCULATE(
    SUMX(
        match_performance_logs,
        IF(
            match_performance_logs[is_selected],
            IF(
                match_performance_logs[is_captain],
                match_performance_logs[actual_fantasy_points] * 2,
                IF(
                    match_performance_logs[is_vice_captain],
                    match_performance_logs[actual_fantasy_points] * 1.5,
                    match_performance_logs[actual_fantasy_points]
                )
            ),
            0
        )
    )
)

## Dashboard Layout & Visualizations
* **Card Visual:** Total Lineup Score vs. Field Average.
* **Scatter Plot:** Projected Points (X-axis) vs. Actual Points (Y-axis) colored by Ownership tier to spot value inefficiencies.
* **Matrix Table:** Full 11-player roster breakdown with conditional formatting on Projection Error.
