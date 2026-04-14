# app.py
import os
import sys
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, make_response
from concurrent.futures import ThreadPoolExecutor

# Add project root to path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.predict import predict_diet
from src.document_extractor import extract_health_data
from src.translations import ui_texts, diet_translations

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------ Language helper ------------------
def get_lang_from_request():
    """Get language from query string, form, or cookie, default 'en'."""
    lang = request.args.get('lang')
    if lang:
        return lang if lang in ui_texts else 'en'
    lang = request.form.get('lang')
    if lang and lang in ui_texts:
        return lang
    lang = request.cookies.get('lang')
    if lang and lang in ui_texts:
        return lang
    return 'en'

# ------------------ Routes ------------------
@app.route('/')
def index():
    lang = get_lang_from_request()
    resp = make_response(render_template('index.html',
                                         lang=lang,
                                         texts=ui_texts[lang],
                                         extracted=None,
                                         upload_error=None))
    resp.set_cookie('lang', lang, max_age=60*60*24*30)  # 30 days
    return resp

@app.route('/upload', methods=['POST'])
def upload_report():
    """Single file upload – extracts data and pre‑fills the form."""
    lang = get_lang_from_request()
    if 'file' not in request.files:
        return render_template('index.html', lang=lang, texts=ui_texts[lang],
                               extracted=None, upload_error="No file part"), 400
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', lang=lang, texts=ui_texts[lang],
                               extracted=None, upload_error="No selected file"), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            extracted_data = extract_health_data(filepath)
            print("Extraction complete. Data:", extracted_data)
        except Exception as e:
            print(f"Extraction error: {e}")
            extracted_data = {}
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

        if not extracted_data or all(v == 0 or v == 'None' or v == 'No'
                                     for v in extracted_data.values() if v is not None):
            return render_template('index.html', lang=lang, texts=ui_texts[lang],
                                   extracted=None,
                                   upload_error="❌ Could not extract data from file. Please fill manually.")

        return render_template('index.html', lang=lang, texts=ui_texts[lang],
                               extracted=extracted_data, upload_error=None)
    else:
        return render_template('index.html', lang=lang, texts=ui_texts[lang],
                               extracted=None,
                               upload_error="Invalid file type. Please upload PDF, PNG, JPG."), 400

@app.route('/upload-multiple', methods=['POST'])
def upload_multiple():
    lang = get_lang_from_request()
    if 'files' not in request.files:
        return "No files uploaded", 400

    files = request.files.getlist('files')
    if len(files) > 10:
        return "Maximum 10 files allowed", 400

    all_results = []
    errors = []

    for file in files:
        if file.filename == '':
            continue
        if not allowed_file(file.filename):
            errors.append(f"{file.filename}: Invalid file type")
            continue

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            extracted = extract_health_data(filepath)
            print(f"\n--- Extracted data for {filename} ---")
            print(extracted)
            print("------------------------------------\n")

            # If extraction returned nothing, assign safe defaults
            if not extracted:
                extracted = {}

            # Ensure all required keys exist with defaults
            required_keys = [
                'Age', 'Gender', 'Height_cm', 'Weight_kg', 'BMI',
                'Blood_Pressure_Systolic', 'Blood_Pressure_Diastolic',
                'Cholesterol_Level', 'Blood_Sugar_Level', 'Chronic_Disease',
                'Genetic_Risk_Factor', 'Allergies', 'Food_Aversions',
                'Daily_Steps', 'Exercise_Frequency', 'Sleep_Hours',
                'Alcohol_Consumption', 'Smoking_Habit', 'Dietary_Habits',
                'Preferred_Cuisine', 'Caloric_Intake', 'Protein_Intake',
                'Carbohydrate_Intake', 'Fat_Intake'
            ]
            for key in required_keys:
                if key not in extracted:
                    # Categorical defaults
                    if key in ['Gender', 'Chronic_Disease', 'Allergies', 'Food_Aversions',
                               'Dietary_Habits', 'Preferred_Cuisine', 'Alcohol_Consumption',
                               'Smoking_Habit', 'Genetic_Risk_Factor']:
                        extracted[key] = 'None'
                    else:
                        extracted[key] = 0

            # Predict diet for this patient
            diet_plan, severity, precautions = predict_diet(extracted, lang=lang)

            all_results.append({
                'filename': file.filename,
                'extracted': extracted,
                'diet_plan': diet_plan,
                'severity': severity,
                'precautions': precautions
            })
        except Exception as e:
            print(f"❌ ERROR processing {filename}: {str(e)}")
            errors.append(f"{file.filename}: {str(e)}")
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    return render_template('multi_result.html', results=all_results, errors=errors, lang=lang)

@app.route('/analyze', methods=['POST'])
def analyze():
    lang = get_lang_from_request()

    # Collect form data (same field names as in index.html)
    input_data = {
        'Age': int(request.form['age']),
        'Gender': request.form['gender'],
        'Height_cm': float(request.form['height']),
        'Weight_kg': float(request.form['weight']),
        'BMI': float(request.form['bmi']),
        'Chronic_Disease': request.form['chronic_disease'],
        'Blood_Pressure_Systolic': int(request.form['bp_sys']),
        'Blood_Pressure_Diastolic': int(request.form['bp_dia']),
        'Cholesterol_Level': int(request.form['cholesterol']),
        'Blood_Sugar_Level': int(request.form['glucose']),
        'Genetic_Risk_Factor': request.form['genetic_risk'],
        'Allergies': request.form['allergies'],
        'Daily_Steps': int(request.form['steps']),
        'Exercise_Frequency': int(request.form['exercise_freq']),
        'Sleep_Hours': float(request.form['sleep']),
        'Alcohol_Consumption': request.form['alcohol'],
        'Smoking_Habit': request.form['smoking'],
        'Dietary_Habits': request.form['dietary_habits'],
        'Caloric_Intake': int(request.form['calories']),
        'Protein_Intake': int(request.form['protein']),
        'Carbohydrate_Intake': int(request.form['carbs']),
        'Fat_Intake': int(request.form['fats']),
        'Preferred_Cuisine': request.form['cuisine'],
        'Food_Aversions': request.form['aversions']
    }

    # Get prediction, severity, and precautions
    diet_plan, severity, precautions = predict_diet(input_data, lang=lang)

    # Translate diet plan name
    diet_plan_translated = diet_translations[lang].get(diet_plan, diet_plan)

    # Generate simplified health summary with colour coding
    explanation = f"""
    <h3>{'📊 Your Health Summary' if lang=='en' else '📊 आपका स्वास्थ्य सारांश'}</h3>
    <ul>
        <li>{'Blood Pressure' if lang=='en' else 'रक्तचाप'}: {severity['bp'][0]} <span style='color:{severity['bp'][1]}'>●</span></li>
        <li>{'Blood Sugar' if lang=='en' else 'रक्त शर्करा'}: {severity['glucose'][0]} <span style='color:{severity['glucose'][1]}'>●</span></li>
        <li>{'Cholesterol' if lang=='en' else 'कोलेस्ट्रॉल'}: {severity['cholesterol'][0]} <span style='color:{severity['cholesterol'][1]}'>●</span></li>
        <li>{'BMI' if lang=='en' else 'बीएमआई'}: {severity['bmi'][0]} <span style='color:{severity['bmi'][1]}'>●</span></li>
    </ul>
    <p>⚠️ <strong>{'Critical alerts:' if lang=='en' else 'महत्वपूर्ण चेतावनी:'}</strong> {
        'None' if all(s[0] in ['Normal','सामान्य','Desirable','वांछनीय'] for s in severity.values())
        else ('Please pay attention to the highlighted parameters above.' if lang=='en' else 'कृपया ऊपर हाइलाइट किए गए मापदंडों पर ध्यान दें।')
    }</p>
    """

    diet_text = f"""
    <h3>{'🍽️ Recommended Meal Plan:' if lang=='en' else '🍽️ अनुशंसित आहार योजना:'} <span style='color:#2c7da0'>{diet_plan_translated}</span></h3>
    <p>{'Based on your health profile, we suggest a' if lang=='en' else 'आपके स्वास्थ्य प्रोफ़ाइल के आधार पर, हम सुझाव देते हैं'} {diet_plan_translated.lower()}. 
    {'Focus on whole foods, portion control, and regular meal timings.' if lang=='en' else 'संपूर्ण खाद्य पदार्थों, भाग नियंत्रण और नियमित भोजन समय पर ध्यान दें।'}</p>
    """

    precaution_text = f"<h3>{'🛡️ Precautions & Tips' if lang=='en' else '🛡️ सावधानियाँ और सुझाव'}</h3><ul>" + "".join(f"<li>{p}</li>" for p in precautions) + "</ul>"

    return render_template('result.html',
                           explanation=explanation,
                           diet_plan=diet_text,
                           precautions=precaution_text,
                           lang=lang)

if __name__ == '__main__':
    app.run(debug=True)