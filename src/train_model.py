# src/train_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb
import joblib

# Load dataset
df = pd.read_csv('dataset/Personalized_Diet_Recommendations.csv')
print(f"Initial shape: {df.shape}")

# Drop identifier
df.drop('Patient_ID', axis=1, inplace=True)

# Remove leaky columns (recommended macros) and redundant intake columns
leaky_cols = ['Recommended_Calories', 'Recommended_Protein', 'Recommended_Carbs', 'Recommended_Fats']
intake_cols = ['Caloric_Intake', 'Protein_Intake', 'Carbohydrate_Intake', 'Fat_Intake']
df.drop(leaky_cols + intake_cols, axis=1, inplace=True)

# Drop height/weight (BMI already captures this)
df.drop(['Height_cm', 'Weight_kg'], axis=1, inplace=True)

# ----------------- Feature Engineering -----------------
# BMI Category
def bmi_cat(bmi):
    if bmi < 18.5: return 'Underweight'
    elif bmi < 25: return 'Normal'
    elif bmi < 30: return 'Overweight'
    else: return 'Obese'
df['BMI_Category'] = df['BMI'].apply(bmi_cat)

# Blood Pressure Category
def bp_cat(sbp, dbp):
    if sbp < 120 and dbp < 80: return 'Normal'
    elif sbp < 130 and dbp < 80: return 'Elevated'
    elif sbp < 140 or dbp < 90: return 'Stage1_Hypertension'
    else: return 'Stage2_Hypertension'
df['BP_Category'] = df.apply(lambda x: bp_cat(x['Blood_Pressure_Systolic'], x['Blood_Pressure_Diastolic']), axis=1)

# Blood Sugar Category
def glucose_cat(glu):
    if glu < 100: return 'Normal'
    elif glu < 126: return 'Prediabetes'
    else: return 'Diabetes'
df['Glucose_Category'] = df['Blood_Sugar_Level'].apply(glucose_cat)

# Age Group
def age_group(age):
    if age < 30: return 'Young'
    elif age < 60: return 'Adult'
    else: return 'Senior'
df['Age_Group'] = df['Age'].apply(age_group)

# Lifestyle Score (steps + exercise_freq*1000 + sleep*500)
df['Lifestyle_Score'] = df['Daily_Steps'] + df['Exercise_Frequency'] * 1000 + df['Sleep_Hours'] * 500

# Drop original continuous columns that are now replaced by categories (optional but helps)
# Keep them for now; the model can use both.

print(f"Shape after feature engineering: {df.shape}")

# ----------------- Target -----------------
target = 'Recommended_Meal_Plan'

# ----------------- Encode categoricals -----------------
categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
categorical_cols.remove(target)
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

# Encode target
target_encoder = LabelEncoder()
y = target_encoder.fit_transform(df[target])

# Features (all except target)
X = df.drop(target, axis=1)

# Scale numerical features
numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
scaler = StandardScaler()
X[numerical_cols] = scaler.fit_transform(X[numerical_cols])

# Train/test split (stratify to preserve class balance)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")

# ----------------- XGBoost with Hyperparameter Tuning -----------------
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [4, 6, 8, 10],
    'learning_rate': [0.01, 0.05, 0.1],
    'subsample': [0.7, 0.8, 0.9],
    'colsample_bytree': [0.7, 0.8, 0.9],
    'gamma': [0, 0.1, 0.2]
}
xgb_model = xgb.XGBClassifier(random_state=42, eval_metric='mlogloss', use_label_encoder=False)
search = RandomizedSearchCV(xgb_model, param_grid, n_iter=30, cv=5, scoring='accuracy', n_jobs=-1, random_state=42, verbose=1)
search.fit(X_train, y_train)

best_model = search.best_estimator_
print(f"\nBest parameters: {search.best_params_}")
print(f"Best cross‑validation accuracy: {search.best_score_:.3f}")

# Evaluate on test set
y_pred = best_model.predict(X_test)
test_acc = accuracy_score(y_test, y_pred)
print(f"\n✅ Test set accuracy: {test_acc:.2%}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=target_encoder.classes_))

# ----------------- Save artifacts -----------------
joblib.dump(best_model, 'models/diet_xgb_model.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
joblib.dump(label_encoders, 'models/label_encoders.pkl')
joblib.dump(target_encoder, 'models/target_encoder.pkl')
print("\n✅ Model and preprocessors saved to 'models/' folder.")