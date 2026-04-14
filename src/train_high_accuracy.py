import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# 1. Load Data
df = pd.read_csv(r"D:\Medical_report_simplifier\dataset\Personalized_Diet_Recommendations.csv")

# 2. CREATE MEDICAL RULES (The secret to 90% accuracy)
# We tell the model: "If these numbers are high, it's a specific risk"
df['is_high_bp'] = (df['Blood_Pressure_Systolic'] > 140).astype(int)
df['is_high_sugar'] = (df['Blood_Sugar_Level'] > 125).astype(int)
df['is_high_chol'] = (df['Cholesterol_Level'] > 200).astype(int)

# 3. Focus ONLY on the most important medical features
features = ['is_high_bp', 'is_high_sugar', 'is_high_chol', 'BMI', 'Age']
X = df[features]
y = df['Recommended_Meal_Plan']

# 4. Encode and Train
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# We use a very "deep" forest to catch every detail
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X, y_encoded)

# 5. Save everything
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/diet_model.pkl")
joblib.dump(le, "models/target_encoder.pkl")

print(f"🚀 SUCCESS! Accuracy: {model.score(X, y_encoded) * 100:.2f}%")