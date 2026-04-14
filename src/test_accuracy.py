import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score
import xgboost as xgb

df = pd.read_csv('dataset/Personalized_Diet_Recommendations.csv')
df.drop('Patient_ID', axis=1, inplace=True)

# Remove leaky and intake columns
leaky_cols = ['Recommended_Calories', 'Recommended_Protein', 'Recommended_Carbs', 'Recommended_Fats']
intake_cols = ['Caloric_Intake', 'Protein_Intake', 'Carbohydrate_Intake', 'Fat_Intake']
df.drop(leaky_cols + intake_cols, axis=1, inplace=True)
df.drop(['Height_cm', 'Weight_kg'], axis=1, inplace=True)

# Feature engineering (same as before)
def bmi_cat(bmi):
    if bmi < 18.5: return 'Underweight'
    elif bmi < 25: return 'Normal'
    elif bmi < 30: return 'Overweight'
    else: return 'Obese'
df['BMI_Category'] = df['BMI'].apply(bmi_cat)

def bp_cat(sbp, dbp):
    if sbp < 120 and dbp < 80: return 'Normal'
    elif sbp < 130 and dbp < 80: return 'Elevated'
    elif sbp < 140 or dbp < 90: return 'Stage1_Hypertension'
    else: return 'Stage2_Hypertension'
df['BP_Category'] = df.apply(lambda x: bp_cat(x['Blood_Pressure_Systolic'], x['Blood_Pressure_Diastolic']), axis=1)

def glucose_cat(glu):
    if glu < 100: return 'Normal'
    elif glu < 126: return 'Prediabetes'
    else: return 'Diabetes'
df['Glucose_Category'] = df['Blood_Sugar_Level'].apply(glucose_cat)

def age_group(age):
    if age < 30: return 'Young'
    elif age < 60: return 'Adult'
    else: return 'Senior'
df['Age_Group'] = df['Age'].apply(age_group)

df['Lifestyle_Score'] = df['Daily_Steps'] + df['Exercise_Frequency'] * 1000 + df['Sleep_Hours'] * 500

# Encode categoricals
target = 'Recommended_Meal_Plan'
categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
categorical_cols.remove(target)
for col in categorical_cols:
    df[col] = LabelEncoder().fit_transform(df[col].astype(str))

# Encode target
target_encoder = LabelEncoder()
y = target_encoder.fit_transform(df[target])
X = df.drop(target, axis=1)

# Scale numericals
numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
X[numerical_cols] = StandardScaler().fit_transform(X[numerical_cols])

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Simple XGBoost (no hyperparameter search)
model = xgb.XGBClassifier(n_estimators=300, max_depth=8, learning_rate=0.05, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Test Accuracy: {acc:.2%}")