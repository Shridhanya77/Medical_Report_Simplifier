# src/predict.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import joblib
from utils import assess_severity, get_precautions

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'models')

def load_artifacts():
    macro_models = joblib.load(os.path.join(MODEL_DIR, 'macro_models.pkl'))
    classifier = joblib.load(os.path.join(MODEL_DIR, 'macro_classifier.pkl'))
    scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
    label_encoders = joblib.load(os.path.join(MODEL_DIR, 'label_encoders.pkl'))
    plan_encoder = joblib.load(os.path.join(MODEL_DIR, 'plan_encoder.pkl'))
    return macro_models, classifier, scaler, label_encoders, plan_encoder

def predict_diet(input_dict, lang='en'):
    macro_models, classifier, scaler, label_encoders, plan_encoder = load_artifacts()
    
    # Convert input to DataFrame
    df_input = pd.DataFrame([input_dict])
    
    # Drop columns not used in training (if present)
    drop_cols = ['Recommended_Calories', 'Recommended_Protein', 'Recommended_Carbs', 'Recommended_Fats',
                 'Caloric_Intake', 'Protein_Intake', 'Carbohydrate_Intake', 'Fat_Intake',
                 'Height_cm', 'Weight_kg']
    for col in drop_cols:
        if col in df_input.columns:
            df_input.drop(col, axis=1, inplace=True)
    
    # Ensure all expected feature columns are present
    expected_cols = scaler.feature_names_in_
    for col in expected_cols:
        if col not in df_input.columns:
            df_input[col] = 0
    
    df_input = df_input[expected_cols]
    
    # Encode categoricals using saved label encoders
    for col, le in label_encoders.items():
        if col in df_input.columns:
            try:
                df_input[col] = le.transform(df_input[col].astype(str))
            except ValueError:
                df_input[col] = 0
    
    # Scale features
    df_input_scaled = scaler.transform(df_input)
    
    # Predict recommended macros
    pred_macros = []
    for col in ['Recommended_Calories', 'Recommended_Protein', 'Recommended_Carbs', 'Recommended_Fats']:
        pred_val = macro_models[col].predict(df_input_scaled)[0]
        pred_macros.append(pred_val)
    pred_macros = np.array(pred_macros).reshape(1, -1)
    
    # Predict diet plan from predicted macros
    pred_plan_enc = classifier.predict(pred_macros)[0]
    diet_plan = plan_encoder.inverse_transform([pred_plan_enc])[0]
    
    # Severity (unchanged)
    severity = assess_severity(
        input_dict.get('Blood_Pressure_Systolic', 120),
        input_dict.get('Blood_Pressure_Diastolic', 80),
        input_dict.get('Blood_Sugar_Level', 100),
        input_dict.get('Cholesterol_Level', 200),
        input_dict.get('BMI', 22),
        lang=lang
    )
    
    # Precautions (unchanged)
    precautions = get_precautions(
        input_dict.get('Chronic_Disease', 'None'),
        input_dict.get('Allergies', 'None'),
        input_dict.get('Food_Aversions', 'None'),
        lang=lang
    )
    
    return diet_plan, severity, precautions