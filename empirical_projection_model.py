import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

def generate_empirical_features(df_players, historical_logs):
    """
    Merges live player rosters with historical logs to extract rolling metrics,
    venue performance, and strike rates.
    """
    # Merge active roster with historical aggregated stats
    merged = pd.merge(df_players, historical_logs, on="name", how="left", suffixes=('', '_hist'))
    
    # Handle rookies or players with sparse historical records using role-based medians
    merged['rolling_avg_pts'] = merged['rolling_avg_pts'].fillna(merged.groupby('role')['rolling_avg_pts'].transform('median'))
    merged['venue_avg_pts'] = merged['venue_avg_pts'].fillna(merged['rolling_avg_pts'] * 0.95)
    merged['strike_rate'] = merged['strike_rate'].fillna(120.0)
    merged['economy_rate'] = merged['economy_rate'].fillna(8.0)
    merged['opposition_factor'] = merged['opposition_factor'].fillna(1.0)
    
    return merged

def train_and_predict_projections(current_players_df, historical_training_df):
    """
    Trains a Gradient Boosting regression baseline to predict empirical fantasy points
    and assign dynamic player salary costs based on predictive value tiers.
    """
    feature_columns = [
        'rolling_avg_pts', 
        'venue_avg_pts', 
        'strike_rate', 
        'economy_rate', 
        'opposition_factor'
    ]
    target_column = 'actual_fantasy_pts'

    # Build ML Pipeline
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', GradientBoostingRegressor(n_estimators=150, learning_rate=0.05, max_depth=4, random_state=42))
    ])

    # If historical training data is available, fit the model
    if not historical_training_df.empty and target_column in historical_training_df.columns:
        X_train = historical_training_df[feature_columns]
        y_train = historical_training_df[target_column]
        model.fit(X_train, y_train)
        
        # Predict on active match feature set
        current_features = current_players_df[feature_columns]
        current_players_df['proj_points'] = model.predict(current_features).round(1)
    else:
        # Fallback empirical multi-factor weighted scoring model
        current_players_df['proj_points'] = (
            (current_players_df['rolling_avg_pts'] * 0.45) +
            (current_players_df['venue_avg_pts'] * 0.35) +
            (current_players_df['strike_rate'] * 0.20)
        ).round(1)

    # Dynamic Salary Cost Assignment based on predicted points tiers
    def assign_dynamic_cost(row):
        pts = row['proj_points']
        role = row['role']
        if pts > 110:
            return 10.5 if role in ['WK', 'BAT'] else 10.0
        elif pts > 85:
            return 9.5 if role in ['BAT', 'AR'] else 9.0
        elif pts > 65:
            return 8.5
        else:
            return 7.5

    current_players_df['cost'] = current_players_df.apply(assign_dynamic_cost, axis=1)
    
    return current_players_df[['name', 'role', 'team', 'cost', 'proj_points']]
