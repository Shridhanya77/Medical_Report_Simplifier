# src/utils.py
from translations import severity_translations, precautions_translations

def assess_severity(bp_sys, bp_dia, glucose, cholesterol, bmi, lang='en'):
    severity = {}
    
    # Blood pressure
    if bp_sys < 120 and bp_dia < 80:
        severity['bp'] = (severity_translations[lang]['Normal'], 'green')
    elif bp_sys < 130 and bp_dia < 80:
        severity['bp'] = (severity_translations[lang]['Elevated'], 'yellow')
    elif bp_sys < 140 or bp_dia < 90:
        severity['bp'] = (severity_translations[lang]['Stage 1 Hypertension'], 'orange')
    else:
        severity['bp'] = (severity_translations[lang]['Stage 2 Hypertension'], 'red')
    
    # Blood sugar
    if glucose < 100:
        severity['glucose'] = (severity_translations[lang]['Normal'], 'green')
    elif glucose < 126:
        severity['glucose'] = (severity_translations[lang]['Prediabetes'], 'yellow')
    else:
        severity['glucose'] = (severity_translations[lang]['Diabetes'], 'red')
    
    # Cholesterol
    if cholesterol < 200:
        severity['cholesterol'] = (severity_translations[lang]['Desirable'], 'green')
    elif cholesterol < 240:
        severity['cholesterol'] = (severity_translations[lang]['Borderline High'], 'yellow')
    else:
        severity['cholesterol'] = (severity_translations[lang]['High'], 'red')
    
    # BMI
    if bmi < 18.5:
        severity['bmi'] = (severity_translations[lang]['Underweight'], 'yellow')
    elif bmi < 25:
        severity['bmi'] = (severity_translations[lang]['Normal'], 'green')
    elif bmi < 30:
        severity['bmi'] = (severity_translations[lang]['Overweight'], 'yellow')
    else:
        severity['bmi'] = (severity_translations[lang]['Obese'], 'red')
    
    return severity

def get_precautions(chronic_disease, allergies, aversions, lang='en'):
    precautions = []
    
    if chronic_disease == 'Hypertension':
        precautions.append(precautions_translations[lang]['reduce_sodium'])
        precautions.append(precautions_translations[lang]['increase_potassium'])
        precautions.append(precautions_translations[lang]['limit_alcohol'])
    elif chronic_disease == 'Diabetes':
        precautions.append(precautions_translations[lang]['monitor_carbs'])
        precautions.append(precautions_translations[lang]['low_gi'])
        precautions.append(precautions_translations[lang]['exercise_sugar'])
    elif chronic_disease == 'Heart Disease':
        precautions.append(precautions_translations[lang]['healthy_fats'])
        precautions.append(precautions_translations[lang]['omega3'])
        precautions.append(precautions_translations[lang]['avoid_trans'])
    elif chronic_disease == 'Obesity':
        precautions.append(precautions_translations[lang]['calorie_deficit'])
        precautions.append(precautions_translations[lang]['increase_fiber'])
        precautions.append(precautions_translations[lang]['exercise_weight'])
    
    if allergies and allergies.lower() != 'none':
        precautions.append(f'🔹 Avoid: {allergies}')
    if aversions and aversions.lower() != 'none':
        precautions.append(f'🔹 You dislike: {aversions}')
    
    return precautions