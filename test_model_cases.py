import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

def create_test_cases():
    # Create comprehensive test cases based on user story requirements
    test_cases = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=10, freq='D'),
        'time': ['08:00', '17:30', '22:00', '15:00', '07:30', '19:00', '13:00', '23:00', '16:00', '12:00'],
        'road_type': [6, 6, 3, 1, 2, 6, 3, 6, 2, 1],  # Various road types for comparison
        'weather_conditions': ['Fine', 'Rain', 'Snow', 'Fine', 'Rain', 'Fine', 'Fine', 'Fog', 'Rain', 'Fine'],
        'speed_limit': [30, 60, 70, 40, 30, 50, 40, 60, 50, 40],
        'day_of_week': ['Monday', 'Friday', 'Saturday', 'Wednesday', 'Monday', 'Thursday', 'Tuesday', 'Friday', 'Wednesday', 'Monday'],
        'number_of_vehicles': [2, 3, 1, 2, 2, 4, 2, 1, 2, 2],
        'number_of_casualties': [1, 2, 1, 1, 1, 3, 1, 1, 1, 1],
        'light_conditions': ['Daylight', 'Daylight', 'Darkness', 'Daylight', 'Dawn', 'Dusk', 'Daylight', 'Darkness', 'Daylight', 'Daylight'],
        'road_surface_conditions': ['Dry', 'Wet', 'Snow', 'Dry', 'Wet', 'Dry', 'Dry', 'Wet', 'Wet', 'Dry'],
        'junction_detail': ['T Junction', 'Crossroads', 'Not at junction', 'Roundabout', 'T Junction', 'Crossroads', 'T Junction', 'Not at junction', 'Roundabout', 'T Junction'],
        'description': [
            'School zone during morning rush',
            'High-traffic urban area during evening rush',
            'Rural road in adverse weather',
            'Residential area with moderate traffic',
            'School zone in wet conditions',
            'Urban area with multiple vehicles',
            'Commercial area during lunch hour',
            'Night driving in poor visibility',
            'Suburban area in rain',
            'Typical daytime conditions'
        ]
    })
    return test_cases

def load_and_prepare_model():
    print("Loading pre-trained model...")
    model_artifacts = joblib.load('best_model.joblib')
    return model_artifacts['model'], model_artifacts['feature_names']

def prepare_features(df, feature_names):
    print("\nPreparing features...")
    # Categorical columns
    cat_cols = ['weather_conditions', 'day_of_week', 'light_conditions', 
                'road_surface_conditions', 'junction_detail']
    
    # Create dummy variables
    df_encoded = pd.get_dummies(df, columns=cat_cols)
    
    # Ensure all expected feature columns are present
    for col in feature_names:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    
    # Numeric columns to scale
    num_cols = ['speed_limit', 'number_of_vehicles', 'number_of_casualties']
    scaler = StandardScaler()
    df_encoded[num_cols] = scaler.fit_transform(df_encoded[num_cols])
    
    # Select only the features used by the model
    return df_encoded[feature_names]

def create_risk_heatmap(predictions, test_cases):
    print("\nGenerating risk heatmap...")
    # Create a matrix of features vs risk
    risk_data = pd.DataFrame({
        'Risk_Score': predictions,
        'Road_Type': test_cases['road_type'],
        'Speed_Limit': test_cases['speed_limit'],
        'Weather': test_cases['weather_conditions']
    })
    
    # Create pivot table for heatmap
    pivot_table = pd.pivot_table(risk_data, values='Risk_Score', 
                               index='Road_Type', columns='Weather', 
                               aggfunc='mean')
    
    # Create heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_table, annot=True, cmap='RdYlGn_r', fmt='.2f')
    plt.title('Accident Risk Heatmap by Road Type and Weather')
    plt.tight_layout()
    plt.savefig('risk_heatmap.png')
    plt.close()

def main():
    # Create test cases
    test_cases = create_test_cases()
    
    # Load and prepare model
    model, feature_names = load_and_prepare_model()
    
    # Prepare features
    features = prepare_features(test_cases, feature_names)
    
    # Make predictions
    print("\nMaking predictions...")
    risk_probabilities = model.predict_proba(features)[:, 1]  # Probability of high risk
    predictions = model.predict(features)
    
    # Create visualization
    create_risk_heatmap(risk_probabilities, test_cases)
    
    # Print results with recommendations
    print("\nRisk Assessment Results:")
    print("=" * 80)
    for i, (prob, pred, desc) in enumerate(zip(risk_probabilities, predictions, test_cases['description'])):
        risk_level = "High Risk" if prob > 0.7 else "Medium Risk" if prob > 0.3 else "Low Risk"
        print(f"\nScenario {i+1}:")
        print(f"Description: {desc}")
        print(f"Risk Probability: {prob:.2%}")
        print(f"Risk Level: {risk_level}")
        
        # Generate recommendations based on risk level
        if risk_level == "High Risk":
            print("Recommended Interventions:")
            if test_cases.iloc[i]['speed_limit'] > 40:
                print("- Consider reducing speed limit")
            if test_cases.iloc[i]['light_conditions'] == 'Darkness':
                print("- Improve street lighting")
            if test_cases.iloc[i]['junction_detail'] != 'Not at junction':
                print("- Install traffic monitoring cameras")
            print("- Increase police patrols in the area")
    
    print("\nRisk heatmap has been saved as 'risk_heatmap.png'")

if __name__ == "__main__":
    main() 