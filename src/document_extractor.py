# src/document_extractor.py
import re
import pdfplumber
import os

def extract_health_data(file_path):
    print(f"\n📄 Extracting from: {file_path}")
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        print(f"✅ Extracted {len(text)} characters")
    except Exception as e:
        print(f"❌ PDF extraction error: {e}")
        return {}
    
    if not text.strip():
        print("❌ No text found in PDF")
        return {}
    
    # Debug: print first 500 characters
    print("\n📝 Text sample (first 500 chars):\n", text[:500])
    
    data = {}
    
    # Age
    age_match = re.search(r'Age[:\s]*(\d+)', text, re.IGNORECASE)
    data['Age'] = int(age_match.group(1)) if age_match else None
    
    # Gender
    gender_match = re.search(r'Gender[:\s]*(Male|Female|Other)', text, re.IGNORECASE)
    data['Gender'] = gender_match.group(1).capitalize() if gender_match else "Other"
    
    # Height
    height_match = re.search(r'Height[:\s]*(\d+(?:\.\d+)?)\s*(cm|m)', text, re.IGNORECASE)
    if height_match:
        h = float(height_match.group(1))
        if height_match.group(2).lower() == 'm':
            h *= 100
        data['Height_cm'] = h
    else:
        data['Height_cm'] = None
    
    # Weight
    weight_match = re.search(r'Weight[:\s]*(\d+(?:\.\d+)?)\s*(kg|lb)', text, re.IGNORECASE)
    if weight_match:
        w = float(weight_match.group(1))
        if weight_match.group(2).lower() == 'lb':
            w *= 0.453592
        data['Weight_kg'] = w
    else:
        data['Weight_kg'] = None
    
    # BMI
    if data['Height_cm'] and data['Weight_kg']:
        bmi = data['Weight_kg'] / ((data['Height_cm']/100)**2)
        data['BMI'] = round(bmi, 1)
    else:
        data['BMI'] = None
    
    # Blood Pressure
    bp_match = re.search(r'Blood Pressure[:\s]*(\d+)/(\d+)', text, re.IGNORECASE)
    if bp_match:
        data['Blood_Pressure_Systolic'] = int(bp_match.group(1))
        data['Blood_Pressure_Diastolic'] = int(bp_match.group(2))
    else:
        data['Blood_Pressure_Systolic'] = None
        data['Blood_Pressure_Diastolic'] = None
    
    # Cholesterol
    chol_match = re.search(r'Cholesterol[:\s]*(\d+)', text, re.IGNORECASE)
    data['Cholesterol_Level'] = int(chol_match.group(1)) if chol_match else None
    
    # Blood Sugar
    glucose_match = re.search(r'Blood Sugar[:\s]*(\d+)', text, re.IGNORECASE)
    data['Blood_Sugar_Level'] = int(glucose_match.group(1)) if glucose_match else None
    
    # Chronic Disease
    diseases = []
    for disease in ['Hypertension', 'Diabetes', 'Heart Disease', 'Obesity']:
        if re.search(disease, text, re.IGNORECASE):
            diseases.append(disease)
    data['Chronic_Disease'] = diseases[0] if diseases else 'None'
    
    # Genetic Risk Factor
    if re.search(r'Genetic Risk[:\s]*Yes', text, re.IGNORECASE):
        data['Genetic_Risk_Factor'] = 'Yes'
    else:
        data['Genetic_Risk_Factor'] = 'No'
    
    # Allergies
    allergy_match = re.search(r'Allergies?[:\s]*(.*?)(?:\n|$)', text, re.IGNORECASE)
    data['Allergies'] = allergy_match.group(1).strip() if allergy_match else 'None'
    
    # Food Aversions
    aversion_match = re.search(r'Food Aversions?[:\s]*(.*?)(?:\n|$)', text, re.IGNORECASE)
    data['Food_Aversions'] = aversion_match.group(1).strip() if aversion_match else 'None'
    
    # Default lifestyle values (since not in reports)
    data['Daily_Steps'] = 5000
    data['Exercise_Frequency'] = 3
    data['Sleep_Hours'] = 7.0
    data['Alcohol_Consumption'] = 'No'
    data['Smoking_Habit'] = 'No'
    data['Dietary_Habits'] = 'Regular'
    data['Preferred_Cuisine'] = 'Western'
    data['Caloric_Intake'] = 2000
    data['Protein_Intake'] = 100
    data['Carbohydrate_Intake'] = 250
    data['Fat_Intake'] = 70
    
    # Replace None with 0 for numeric fields (to avoid JavaScript issues)
    for key in ['Age', 'Height_cm', 'Weight_kg', 'BMI', 'Blood_Pressure_Systolic', 
                'Blood_Pressure_Diastolic', 'Cholesterol_Level', 'Blood_Sugar_Level']:
        if data.get(key) is None:
            data[key] = 0
    
    print("\n✅ Extracted data:", {k: v for k, v in data.items() if v != 0 and v != 'None' and v != 'No'})
    return data