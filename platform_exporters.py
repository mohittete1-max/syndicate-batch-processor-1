import pandas as pd
import os

def export_platform_templates(portfolio_df, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Primary 10:1 Platform Master Export (Already part of your pipeline)
    master_path = os.path.join(output_dir, "master_gpp_portfolio.csv")
    portfolio_df.to_csv(master_path, index=False)
    
    # 2. Dream11 / My11Circle Bulk Upload Format Converter
    # Typically requires structured lineup slots: Lineup ID, Player Name, Team, Role, Salary
    if {'lineup_id', 'player_name', 'team', 'role', 'salary'}.issubset(portfolio_df.columns):
        d11_df = pd.DataFrame({
            'Lineup_ID': portfolio_df['lineup_id'],
            'Player': portfolio_df['player_name'],
            'Team': portfolio_df['team'],
            'Role': portfolio_df['role'],
            'Salary': portfolio_df['salary']
        })
        
        # Save individual lineup files or a consolidated multi-lineup upload sheet
        d11_path = os.path.join(output_dir, "dream11_bulk_upload.csv")
        d11_df.to_csv(d11_path, index=False)
        print("📁 Multi-platform export templates generated successfully!")

if __name__ == "__main__":
    pass
