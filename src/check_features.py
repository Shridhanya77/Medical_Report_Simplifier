import joblib

# Load the scaler that was saved during training
scaler = joblib.load("models/scaler.pkl")

print("Expected features (in order):")
for i, name in enumerate(scaler.feature_names_in_):
    print(f"{i+1}. {name}")
print(f"\nTotal features expected: {len(scaler.feature_names_in_)}")