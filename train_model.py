import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

def generate_cardio_data(n_samples=5000, random_state=42):
    np.random.seed(random_state)
    
    # 1. Base physiological features
    age = np.random.randint(25, 80, n_samples)
    gender = np.random.choice([0, 1], n_samples)  # 0: Female, 1: Male
    height = np.random.normal(168, 10, n_samples).clip(140, 200)
    weight = np.random.normal(74, 15, n_samples).clip(45, 140)
    
    # Blood pressure correlated with age and weight
    base_bp = 100 + (age - 25) * 0.45 + (weight - 70) * 0.35 + np.random.normal(0, 12, n_samples)
    bp_hi = np.clip(base_bp, 90, 195).round().astype(int)
    bp_lo = np.clip(bp_hi * 0.65 + np.random.normal(0, 7, n_samples), 55, 125).round().astype(int)
    
    # Cholesterol & Glucose (1: Normal, 2: Above Normal, 3: Well Above Normal)
    chol_prob = [0.65, 0.25, 0.10]
    cholesterol = np.random.choice([1, 2, 3], n_samples, p=chol_prob)
    
    gluc_prob = [0.70, 0.20, 0.10]
    glucose = np.random.choice([1, 2, 3], n_samples, p=gluc_prob)
    
    # Lifestyle factors
    smoke = np.random.choice([0, 1], n_samples, p=[0.75, 0.25])
    alco = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    active = np.random.choice([0, 1], n_samples, p=[0.30, 0.70])
    
    # 2. Engineered features exactly matching app1.py
    height_m = height / 100.0
    bmi = weight / (height_m ** 2)
    pulse_pressure = bp_hi - bp_lo
    bp_ratio = bp_hi / np.maximum(bp_lo, 1)
    bp_sum = bp_hi + bp_lo
    age_bp = age * bp_hi
    bmi_age = bmi * age
    pulse_bmi = pulse_pressure / np.maximum(bmi, 1)
    bp_diff = np.abs(bp_hi - bp_lo)
    weight_age = weight / np.maximum(age, 1)
    height_weight = height / np.maximum(weight, 1)
    
    # Realistic cardiovascular disease probability (logistic latent function)
    # Higher age, higher BP, high cholesterol, smoking, high BMI -> increase risk
    logit = (
        -7.0
        + 0.055 * age
        + 0.035 * (bp_hi - 120)
        + 0.025 * (bp_lo - 80)
        + 0.08 * (bmi - 24)
        + 0.65 * (cholesterol - 1)
        + 0.50 * (glucose - 1)
        + 0.70 * smoke
        + 0.35 * alco
        - 0.45 * active
        + 0.20 * gender
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    target = (np.random.rand(n_samples) < prob).astype(int)
    
    features = np.column_stack([
        age, gender, height, weight,
        bp_hi, bp_lo, cholesterol, glucose, smoke, alco,
        active, bmi, pulse_pressure, bp_ratio, bp_sum, age_bp, bmi_age,
        pulse_bmi, bp_diff, weight_age, height_weight
    ])
    
    feature_names = [
        "Age", "Gender", "Height", "Weight", "Systolic BP", "Diastolic BP", 
        "Cholesterol", "Glucose", "Smoking", "Alcohol", "Physical Activity", 
        "BMI", "Pulse Pressure", "BP Ratio", "BP Sum", "Age*BP", "BMI*Age", 
        "Pulse/BMI", "BP Difference", "Weight/Age", "Height/Weight"
    ]
    
    return features, target, feature_names

def train_and_save():
    print("Generating clinically realistic cardiovascular dataset...")
    X, y, feature_names = generate_cardio_data(n_samples=10000)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Fitting standard scaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=9,
        min_samples_split=8,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_prob)
    print(f"Model Training Complete! Accuracy: {acc*100:.2f}%, ROC-AUC: {roc:.3f}")
    
    # Save the exact filenames expected by app1.py
    model_filename = "heart_disease_model (3).pkl"
    scaler_filename = "scaler (2).pkl"
    
    with open(model_filename, "wb") as f:
        pickle.dump(model, f)
    print(f"Saved: {model_filename}")
    
    with open(scaler_filename, "wb") as f:
        pickle.dump(scaler, f)
    print(f"Saved: {scaler_filename}")

if __name__ == "__main__":
    train_and_save()
