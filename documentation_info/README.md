# Road Safety Risk Prediction Model - POC

## Project Overview
This Proof of Concept (POC) demonstrates an AI-driven road safety platform that helps policymakers identify high-risk road segments and recommend appropriate safety interventions. The system uses machine learning to analyze various factors such as road conditions, weather, time of day, and traffic patterns to predict accident risk levels.

## Key Features
- Risk prediction based on multiple environmental factors
- Visual risk assessment through heatmaps
- Automated safety recommendations
- User-friendly web interface
- Data-driven decision support

## Technical Stack
- **Backend**: Python, Flask, Scikit-learn
- **Frontend**: React (Vercel)
- **Deployment**: Render (Backend), Vercel (Frontend)
- **Data Visualization**: Matplotlib, Seaborn
- **Machine Learning**: Random Forest, LightGBM

## Quick Start
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask backend:
   ```bash
   python app.py
   ```
4. Access the web interface at `http://localhost:5000`

## Model Features
The risk prediction model considers:
- Road type and conditions
- Weather conditions
- Time of day
- Speed limits
- Junction types
- Traffic volume
- Historical accident data

## Usage Example
1. Select location parameters
2. Input environmental conditions
3. Click "Predict Risk"
4. Review risk assessment and recommendations

## Future Enhancements
- User authentication system
- Detailed report generation
- Proposal submission system
- Cost-benefit analysis
- Historical trend analysis

## Documentation
- [Deployment Guide](deployment_guide.md)
- [Feature Documentation](features.md)
- [Presentation Guide](presentation_guide.md)

## Contact
[Your Contact Information] 