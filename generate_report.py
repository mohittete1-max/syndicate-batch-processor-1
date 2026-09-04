import pandas as pd
import os

file_path = r'C:\Users\User\OneDrive\Desktop\Cricket\Optimized_Lineups\RTD_vs_ADF_Optimal_XI.csv'
df = pd.read_csv(file_path)

# Ensure Actual_Points exists
if 'Actual_Points' not in df.columns:
    df['Actual_Points'] = [301.6, 210.9, 125.6, 129.3, 121.3, 102.6, 115.7, 110.5, 105.3, 103.2, 110.9][:len(df)]

# Calculate metrics and percentage differences
df['Points_Variance'] = df['Actual_Points'] - df['Final_EV']
df['Variance_Pct'] = ((df['Points_Variance'] / df['Final_EV']) * 100).round(2)

# Save permanently back to CSV
df.to_csv(file_path, index=False)

# Totals
total_ev = df['Final_EV'].sum()
total_actual = df['Actual_Points'].sum()
total_variance = total_actual - total_ev

# Generate updated HTML Dashboard
html_output = r'C:\Users\User\OneDrive\Desktop\Cricket\Optimized_Lineups\Performance_Report.html'

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Fantasy Cricket Performance Audit</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }}
        .container {{ max-width: 1050px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        h2 {{ color: #111; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .cards {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .card {{ flex: 1; background: #f8f9fa; padding: 20px; border-radius: 6px; border-left: 5px solid #007bff; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .card h3 {{ margin: 0; font-size: 14px; color: #666; text-transform: uppercase; }}
        .card p {{ margin: 10px 0 0; font-size: 24px; font-weight: bold; color: #111; }}
        .positive {{ color: #28a745; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #007bff; color: white; }}
        tr:hover {{ background-color: #f1f1f1; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Dream11 Lineup Performance Audit Dashboard</h2>
        <div class="cards">
            <div class="card" style="border-left-color: #6c757d;">
                <h3>Total Projected EV</h3>
                <p>{total_ev:.2f}</p>
            </div>
            <div class="card" style="border-left-color: #17a2b8;">
                <h3>Total Actual Points</h3>
                <p>{total_actual:.2f}</p>
            </div>
            <div class="card" style="border-left-color: #28a745;">
                <h3>Overall Variance</h3>
                <p class="positive">+{total_variance:.2f}</p>
            </div>
        </div>
        <h2>Comprehensive Player Breakdown</h2>
        {df[['name', 'team', 'role', 'credits', 'form_pts', 'Final_EV', 'Actual_Points', 'Points_Variance', 'Variance_Pct']].to_html(index=False, classes='table', border=0)}
    </div>
</body>
</html>
"""

with open(html_output, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Enhanced Dashboard successfully updated at: {html_output}")
