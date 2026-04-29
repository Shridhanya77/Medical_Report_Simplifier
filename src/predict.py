# src/predict.py (Rule‑Based – No ML Model)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import joblib

model = joblib.load("models/macro_classifier.pkl")
from utils import assess_severity, get_precautions

def rule_based_diet(chronic_disease, bmi, glucose, cholesterol):
    """
    Simple clinical rules to recommend a diet plan.
    Returns one of: 'Balanced Diet', 'Low-Carb Diet', 'Low-Fat Diet', 'High-Protein Diet'
    """
    if chronic_disease == 'Diabetes':
        return 'Low-Carb Diet'
    elif chronic_disease == 'Heart Disease':
        return 'Low-Fat Diet'
    elif cholesterol > 240:
        return 'Low-Fat Diet'
    elif bmi >= 30:
        return 'Low-Fat Diet'
    elif glucose >= 100:
        return 'Low-Carb Diet'
    elif bmi < 18.5:
        return 'High-Protein Diet'
    else:
        return 'Balanced Diet'

def predict_diet(input_dict, lang='en'):
    """
    Predict diet plan using rule‑based logic.
    Also returns severity and precautions (unchanged).
    """
    # Extract values from input_dict
    chronic_disease = input_dict.get('Chronic_Disease', 'None')
    bmi = input_dict.get('BMI', 22)
    glucose = input_dict.get('Blood_Sugar_Level', 100)
    cholesterol = input_dict.get('Cholesterol_Level', 200)
    
    # Get diet plan from rules
    diet_plan = rule_based_diet(chronic_disease, bmi, glucose, cholesterol)
    
    # Severity assessment (colour‑coded health summary)
    severity = assess_severity(
        input_dict.get('Blood_Pressure_Systolic', 120),
        input_dict.get('Blood_Pressure_Diastolic', 80),
        glucose,
        cholesterol,
        bmi,
        lang=lang
    )
    
    # Precautions (disease‑specific, allergies, aversions)
    precautions = get_precautions(
        chronic_disease,
        input_dict.get('Allergies', 'None'),
        input_dict.get('Food_Aversions', 'None'),
        lang=lang
    )
    
    return diet_plan, severity, precautions