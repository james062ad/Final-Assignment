import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler

def prepare_features(data):
    """Prepare features using the same preprocessing as training"""
    # Core Temporal Features
    data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y')
    data['time'] = pd.to_datetime(data['time'], format='%H:%M')
    data['hour'] = data['time'].dt.hour
    data['month'] = data['date'].dt.month
    
    # Risk-focused Features
    data['is_night'] = ((data['hour'] >= 22) | (data['hour'] <= 5)).astype(int)
    data['is_rush_hour'] = data['hour'].isin([7, 8, 9, 16, 17, 18]).astype(int)
    data['is_weekend'] = (data['day_of_week'].isin(['Saturday', 'Sunday'])).astype(int)
    
    # Enhanced Risk Factors
    data['casualty_rate'] = data['number_of_casualties'] / data['number_of_vehicles'].clip(lower=1)
    data['high_speed'] = (data['speed_limit'] >= 60).astype(int)
    
    # Weather and Road Risk Scoring
    weather_risk = {1: 0, 2: 2, 3: 4, 4: 2, 5: 4, 6: 6, 7: 5, 8: 1, 9: 3}
    surface_risk = {1: 0, 2: 2, 3: 4, 4: 5, 5: 5}
    
    data['weather_risk'] = data['weather_conditions'].map(weather_risk).fillna(3)
    data['surface_risk'] = data['road_surface_conditions'].map(surface_risk).fillna(2)
    
    # Combined Risk Score
    data['combined_risk'] = (
        data['weather_risk'] + 
        data['surface_risk'] + 
        data['is_night'] * 2 +
        data['high_speed'] * 2
    )
    
    # High-risk Interaction Features
    data['night_speed_risk'] = data['is_night'] * data['high_speed']
    data['weather_speed_risk'] = data['weather_risk'] * data['high_speed']
    
    return data

def main():
    # Load the model and its artifacts
    print("Loading pre-trained model...")
    model_artifacts = joblib.load('best_model.joblib')
    model = model_artifacts['model']
    feature_names = model_artifacts['feature_names']
    categorical_cols = model_artifacts['categorical_cols']
    numeric_cols = model_artifacts['numeric_cols']

    # Load example data (using first few rows of original dataset)
    print("\nLoading example data...")
    df = pd.read_csv('optimized_accident_data.csv').head(5)
    print("\nExample input data:")
    print(df[['date', 'time', 'road_type', 'weather_conditions', 'speed_limit']].to_string())

    # Prepare features
    print("\nPreparing features...")
    df_processed = prepare_features(df)

    # Process categorical columns
    for col in categorical_cols:
        df_processed[col] = df_processed[col].fillna(df_processed[col].mode()[0])

    # Create dummy variables
    df_encoded = pd.get_dummies(df_processed[categorical_cols], columns=categorical_cols)
    
    # Ensure all expected feature columns are present
    cat_features = [col for col in feature_names if any(col.startswith(prefix + '_') for prefix in categorical_cols)]
    for col in cat_features:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    X_cat = df_encoded[cat_features].values

    # Process numeric columns
    for col in numeric_cols:
        df_processed[col] = df_processed[col].fillna(df_processed[col].median())
    X_num = df_processed[numeric_cols].values

    # Scale numeric features
    scaler = StandardScaler()
    X_num_scaled = scaler.fit_transform(X_num)

    # Combine features
    X = np.hstack([X_cat, X_num_scaled])

    # Make predictions
    print("\nMaking predictions...")
    risk_probabilities = model.predict_proba(X)
    predictions = model.predict(X)

    # Print results
    print("\nPrediction Results:")
    print("Row | High Risk Probability | Prediction")
    print("-" * 45)
    for i, (prob, pred) in enumerate(zip(risk_probabilities, predictions)):
        high_risk_prob = prob[1]  # Probability of high risk
        print(f"{i+1:3d} | {high_risk_prob:19.2%} | {'High Risk' if pred == 1 else 'Normal Risk'}")

if __name__ == "__main__":
    main() 