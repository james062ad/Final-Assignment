# Road Accident Risk Classification Model

## Required Files
- `optimized_accident_data.csv` (main dataset)
- `Classification.py` (main script)
- `requirements.txt` (dependencies)

### Optional Pre-trained Model
- `best_model.joblib` (276KB pre-trained model)
  - Include this if you want to:
    - Use the model without retraining
    - Compare new iterations against baseline
    - Ensure consistent performance across environments

### Example Usage Script
- `predict_risk.py` (example script showing how to use the pre-trained model)
  - Demonstrates loading the model
  - Shows feature preprocessing
  - Makes predictions on example data

## Setup Instructions

### Local Environment
1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Choose one:
   ```bash
   # Option A: Train new model
   python Classification.py

   # Option B: Load pre-trained model (if best_model.joblib is included)
   python predict_risk.py  # Run example prediction script
   ```

### Google Colab
1. Upload required files to Colab
2. Install dependencies:
   ```python
   !pip install -r requirements.txt
   ```
3. Choose one:
   ```python
   # Option A: Train new model
   !python Classification.py

   # Option B: Load pre-trained model
   !python predict_risk.py  # Run example prediction script
   ```

## Output Files
The script will generate:
- `best_model.joblib` (trained model)
- `confusion_matrix_binary.png` (model performance visualization)
- `feature_importance_high_risk.png` (feature importance plot)
- `hourly_risk_pattern.png` (time-based risk analysis)
- `policy_insights.txt` (detailed recommendations)

## Model Details
- Binary classification (high-risk vs non-high-risk)
- Uses XGBoost with SMOTE for class balancing
- Includes feature engineering and policy insights
- Overall accuracy: 88%
- Can identify 30% of high-risk situations 