import pandas as pd

def apply_vegas_adjustments(input_csv="live_slate.csv", output_csv="vegas_adjusted_slate.csv"):
    print("Loading base projections and scraping Vegas lines...")
    
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: {input_csv} missing.")
        return
        
    # In a fully automated setup, these would be pulled via a Sportsbook API.
    # For now, we input the implied run totals for the match.
    # E.g., The Over/Under is 350.5, and IND is favored by 20. 
    # IND Implied = 185.25, ENG Implied = 165.25
    vegas_implied_totals = {
        "IND": 190.5,  # High scoring expectation
        "ENG": 155.5   # Struggling against IND bowling
    }
    
    # Standard T20 baseline score for projection normalization
    BASELINE_T20_TOTAL = 160.0 
    
    print("\n=== VEGAS ODDS SHIFT ===")
    
    for index, row in df.iterrows():
        team = row['team']
        role = row['role']
        base_proj = row['projected_points']
        
        # Calculate how much better/worse the team is expected to do vs average
        team_implied = vegas_implied_totals.get(team, BASELINE_T20_TOTAL)
        offensive_shift_factor = team_implied / BASELINE_T20_TOTAL
        
        new_proj = base_proj
        
        # Adjust Batters and Wicket Keepers based on their team's run expectation
        if role in ['BAT', 'WK']:
            new_proj = base_proj * offensive_shift_factor
            
        # Adjust Bowlers based on the OPPONENT'S run expectation 
        # (If opponent is expected to score low, your bowlers are likely taking more wickets)
        elif role == 'BOWL':
            opponent = "ENG" if team == "IND" else "IND"
            opp_implied = vegas_implied_totals.get(opponent, BASELINE_T20_TOTAL)
            defensive_shift_factor = BASELINE_T20_TOTAL / opp_implied
            
            new_proj = base_proj * defensive_shift_factor
            
        # All-Rounders get a blended shift
        elif role == 'AR':
            opponent = "ENG" if team == "IND" else "IND"
            opp_implied = vegas_implied_totals.get(opponent, BASELINE_T20_TOTAL)
            defensive_shift_factor = BASELINE_T20_TOTAL / opp_implied
            
            blended_shift = (offensive_shift_factor + defensive_shift_factor) / 2
            new_proj = base_proj * blended_shift
            
        # Apply the shift to the dataframe
        df.at[index, 'projected_points'] = round(new_proj, 2)
        
        # Log significant movements
        if abs(new_proj - base_proj) > 2.0:
            direction = "⬆️" if new_proj > base_proj else "⬇️"
            print(f"{direction} {row['player']:<16} | Base: {base_proj:<5} | Vegas: {round(new_proj, 2):<5}")

    # Export the adjusted slate
    df.to_csv(output_csv, index=False)
    print(f"\nSuccess! Vegas-adjusted projections exported to {output_csv}.")
    print("Your MILP engines can now read this file to build market-informed lineups.")

if __name__ == "__main__":
    apply_vegas_adjustments()
