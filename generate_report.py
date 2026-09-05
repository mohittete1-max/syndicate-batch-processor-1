import pandas as pd
import plotly.express as px

def generate_html_report(csv_file="fully_compounded_gpp_portfolio.csv"):
    print("Generating interactive Plotly report...")
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: '{csv_file}' not found.")
        return

    # Dynamically separate metadata (id_vars) from the roster spots (value_vars)
    # This prevents KeyErrors no matter how you rename your output columns!
    player_cols = [c for c in df.columns if c.startswith('Player_') or c in ['Captain', 'Vice_Captain']]
    meta_cols = [c for c in df.columns if c not in player_cols]

    # Unpivot data from wide to long format
    melted = df.melt(id_vars=meta_cols, 
                     value_vars=player_cols,
                     value_name='Player', 
                     var_name='Role')
    
    # Calculate overall player frequencies
    exposure = melted['Player'].value_counts().reset_index()
    exposure.columns = ['Player', 'Drafted_Count']
    exposure['Exposure_%'] = (exposure['Drafted_Count'] / len(df)) * 100

    # Build the interactive bar chart
    fig = px.bar(exposure, x='Exposure_%', y='Player', orientation='h', 
                 title='GPP Portfolio Player Risk Exposure',
                 text='Exposure_%', color='Exposure_%', color_continuous_scale='RdYlGn_r')
    
    # Add your 80% maximum risk tripwire
    fig.add_vline(x=80, line_dash="dash", line_color="red", annotation_text="Max Limit (80%)")
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=700)

    # Export as a standalone webpage
    fig.write_html("portfolio_report.html")
    print("Success! Open 'portfolio_report.html' in your browser.")

if __name__ == "__main__":
    generate_html_report()
