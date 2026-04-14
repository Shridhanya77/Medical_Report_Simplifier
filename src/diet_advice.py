# src/diet_advice.py

def get_blood_sugar_advice(glucose_mgdl):
    if glucose_mgdl < 70:
        return {
            'severity': 'critical',
            'simplified': 'Your blood sugar is **too low** (hypoglycemia). This needs immediate attention.',
            'advice': '🔴 **Immediate action:** Eat 15g of fast-acting carbs (e.g., glucose tablets, ½ cup fruit juice, 1 tbsp honey). Recheck after 15 minutes. Then eat a small snack with protein and carbs (e.g., peanut butter crackers).',
            'diet_tips': '✅ Eat small, frequent meals. ✅ Include complex carbs (whole grains, oats). ✅ Avoid skipping meals.'
        }
    elif glucose_mgdl < 100:
        return {
            'severity': 'normal',
            'simplified': 'Your blood sugar is in the normal range.',
            'advice': 'Keep maintaining a balanced diet with regular meals.',
            'diet_tips': '✅ Limit sugary drinks. ✅ Choose whole grains over refined. ✅ Include protein at every meal.'
        }
    elif glucose_mgdl < 126:
        return {
            'severity': 'warning',
            'simplified': 'Your blood sugar is higher than normal (prediabetes).',
            'advice': 'You can prevent diabetes by changing your diet and lifestyle.',
            'diet_tips': '✅ Reduce sugar and refined carbs. ✅ Increase fibre (vegetables, legumes). ✅ Exercise 30 min/day.'
        }
    else:
        return {
            'severity': 'high',
            'simplified': 'Your blood sugar is in the diabetes range.',
            'advice': 'Consult your doctor. Follow a diabetes-friendly diet.',
            'diet_tips': '❌ Avoid white rice, white bread, sweets. ✅ Eat low-GI foods (dal, whole grains, leafy greens). ✅ Monitor carb portions.'
        }

def get_blood_pressure_advice(systolic, diastolic):
    if systolic < 120 and diastolic < 80:
        return {
            'simplified': 'Your blood pressure is normal.',
            'advice': 'Keep up your healthy lifestyle.',
            'diet_tips': '✅ Limit salt. ✅ Eat potassium-rich foods (bananas, spinach).'
        }
    elif systolic < 130 and diastolic < 80:
        return {
            'simplified': 'Your blood pressure is elevated.',
            'advice': 'Start reducing salt and stress.',
            'diet_tips': '✅ DASH diet (fruits, veg, low-fat dairy). ✅ Reduce processed foods.'
        }
    else:
        return {
            'simplified': 'Your blood pressure is high (hypertension).',
            'advice': 'Reduce sodium immediately. Consult a doctor.',
            'diet_tips': '❌ Avoid pickles, chips, canned soups. ✅ Use herbs instead of salt. ✅ Eat more beets, oats, bananas.'
        }

# Similarly for cholesterol and BMI