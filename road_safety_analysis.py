# Road Safety Risk Assessment - Complete Analysis

# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import xgboost as xgb
import lightgbm as lgb
from datetime import datetime
import joblib
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Load and split dataset
print("Loading data and creating holdout set...")
file_path = "optimized_accident_data.csv"
df = pd.read_csv(file_path)

# Create initial holdout set
df_main, df_holdout = train_test_split(df, test_size=0.15, stratify=df["risk_level"], random_state=42)

# Feature engineering function
def create_features(df):
    print("Creating features focused on high-risk patterns...")
    
    # Core Temporal Features
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    df['time'] = pd.to_datetime(df['time'], format='%H:%M')
    df['hour'] = df['time'].dt.hour
    df['month'] = df['date'].dt.month
    
    # Risk-focused Features
    df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)
    df['is_rush_hour'] = df['hour'].isin([7, 8, 9, 16, 17, 18]).astype(int)
    df['is_weekend'] = (df['day_of_week'].isin(['Saturday', 'Sunday'])).astype(int)
    
    # Enhanced Risk Factors
    df['casualty_rate'] = df['number_of_casualties'] / df['number_of_vehicles'].clip(lower=1)
    df['high_speed'] = (df['speed_limit'] >= 60).astype(int)
    
    # Weather and Road Risk Scoring
    weather_risk = {1: 0, 2: 2, 3: 4, 4: 2, 5: 4, 6: 6, 7: 5, 8: 1, 9: 3}
    surface_risk = {1: 0, 2: 2, 3: 4, 4: 5, 5: 5}
    
    df['weather_risk'] = df['weather_conditions'].map(weather_risk).fillna(3)
    df['surface_risk'] = df['road_surface_conditions'].map(surface_risk).fillna(2)
    
    # Combined Risk Score
    df['combined_risk'] = (
        df['weather_risk'] + 
        df['surface_risk'] + 
        df['is_night'] * 2 +
        df['high_speed'] * 2
    )
    
    # High-risk Interaction Features
    df['night_speed_risk'] = df['is_night'] * df['high_speed']
    df['weather_speed_risk'] = df['weather_risk'] * df['high_speed']
    
    print("Feature engineering completed.")
    return df

# Define feature columns
categorical_cols = [
    "road_type", 
    "weather_conditions",
    "light_conditions",
    "road_surface_conditions",
    "junction_detail"
]

numeric_cols = [
    "speed_limit",
    "number_of_vehicles",
    "number_of_casualties",
    "casualty_rate",
    "weather_risk",
    "surface_risk",
    "combined_risk",
    "night_speed_risk",
    "weather_speed_risk",
    "is_night",
    "is_rush_hour",
    "is_weekend",
    "high_speed"
]

# Apply feature engineering
df_main = create_features(df_main)

# Process categorical columns
for col in categorical_cols:
    df_main[col] = df_main[col].fillna(df_main[col].mode()[0])

# Create dummy variables
df_encoded = pd.get_dummies(df_main[categorical_cols], columns=categorical_cols)
X_cat = df_encoded.values

# Process numeric columns
for col in numeric_cols:
    df_main[col] = df_main[col].fillna(df_main[col].median())

X_num = df_main[numeric_cols].values

# Scale numeric features
scaler = StandardScaler()
X_num_scaled = scaler.fit_transform(X_num)

# Combine features
X = np.hstack([X_cat, X_num_scaled])
feature_names = np.concatenate([df_encoded.columns, numeric_cols])

# Encode target
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df_main["risk_level"])

# Convert to binary classification
print("\nConverting to binary classification (high-risk vs non-high-risk)...")
y_binary = (y == 0).astype(int)  # 1 for high-risk (class 0), 0 for others

print("\nOriginal binary class distribution:")
print(f"High-risk (1): {sum(y_binary == 1)}")
print(f"Other (0): {sum(y_binary == 0)}")

# Apply SMOTE for class balancing
print("\nGenerating synthetic data for balanced classes...")
sampling_strategy = 0.5  # Make minority class 50% of majority class
smote = SMOTE(sampling_strategy=sampling_strategy, random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y_binary)

print("\nResampled binary class distribution:")
print(f"High-risk (1): {sum(y_resampled == 1)}")
print(f"Other (0): {sum(y_resampled == 0)}")

# XGBoost parameters
xgb_params = {
    'objective': 'binary:logistic',
    'max_depth': 6,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'min_child_weight': 1,
    'scale_pos_weight': 2,
    'tree_method': 'hist',
    'n_estimators': 100
}

# Train model
print("Training binary classification model...")
model = xgb.XGBClassifier(**xgb_params)
model.fit(X_resampled, y_resampled)

# Process holdout set
print("\nEvaluating on holdout set...")
df_holdout = create_features(df_holdout)

# Process categorical columns
for col in categorical_cols:
    df_holdout[col] = df_holdout[col].fillna(df_holdout[col].mode()[0])

# Create dummy variables for holdout
holdout_encoded = pd.get_dummies(df_holdout[categorical_cols], columns=categorical_cols)
for col in df_encoded.columns:
    if col not in holdout_encoded.columns:
        holdout_encoded[col] = 0
holdout_encoded = holdout_encoded[df_encoded.columns]
X_holdout_cat = holdout_encoded.values

# Process numeric columns
for col in numeric_cols:
    df_holdout[col] = df_holdout[col].fillna(df_holdout[col].median())

X_holdout_num = df_holdout[numeric_cols].values
X_holdout_num_scaled = scaler.transform(X_holdout_num)
X_holdout = np.hstack([X_holdout_cat, X_holdout_num_scaled])

# Encode holdout targets
y_holdout = label_encoder.transform(df_holdout["risk_level"])
y_holdout_binary = (y_holdout == 0).astype(int)

# Make predictions
y_holdout_pred = model.predict(X_holdout)
y_holdout_pred_proba = model.predict_proba(X_holdout)

# Print metrics
print("\nHoldout Set Metrics:")
print("\nClassification Report:")
print(classification_report(y_holdout_binary, y_holdout_pred))
print(f"ROC AUC: {roc_auc_score(y_holdout_binary, y_holdout_pred_proba[:, 1]):.3f}")

# Create confusion matrix visualization
cm = confusion_matrix(y_holdout_binary, y_holdout_pred)
plt.figure(figsize=(8, 6))
plt.imshow(cm, interpolation='nearest', cmap='Blues')
plt.title('Confusion Matrix - Holdout Set (Binary Classification)')
plt.colorbar()

classes = ['Non-High-Risk', 'High-Risk']
tick_marks = np.arange(len(classes))
plt.xticks(tick_marks, classes, rotation=45)
plt.yticks(tick_marks, classes)

# Add normalized values
cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
for i, j in np.ndindex(cm.shape):
    plt.text(j, i, f'{cm[i, j]}\n({cm_normalized[i, j]:.2%})',
             ha="center", va="center", color="black")

plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig('confusion_matrix_binary.png')
plt.close()

# Create feature importance visualization
importance = model.feature_importances_
indices = np.argsort(importance)[-10:][::-1]

plt.figure(figsize=(10, 6))
plt.title('Top 10 Most Important Features')
plt.bar(range(10), importance[indices])
plt.xticks(range(10), feature_names[indices], rotation=45, ha='right')
plt.tight_layout()
plt.savefig('feature_importance_high_risk.png')
plt.close()

# Save model
joblib.dump(model, 'best_model.joblib')
print("\nModel saved as 'best_model.joblib'")

# Test predictions
test_scenarios = [
    {
        "road_type": 3,
        "weather": "Snow",
        "speed_limit": 70,
        "time_of_day": "Night",
        "junction_detail": "Roundabout"
    },
    {
        "road_type": 1,
        "weather": "Fine",
        "speed_limit": 20,
        "time_of_day": "Afternoon",
        "junction_detail": "Not at junction"
    }
]

def process_scenario(scenario):
    # Convert scenario to DataFrame
    df_scenario = pd.DataFrame([scenario])
    
    # Apply feature engineering
    df_scenario = create_features(df_scenario)
    
    # Process features similar to training data
    # [Add processing code here]
    
    return df_scenario

# Test each scenario
for scenario in test_scenarios:
    processed_scenario = process_scenario(scenario)
    prediction = model.predict_proba(processed_scenario)[0]
    print(f"\nScenario: {scenario}")
    print(f"Risk Probability: {prediction[1]:.2%}")

print("\nAnalysis complete!") 