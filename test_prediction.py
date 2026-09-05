import pickle
import numpy as np
import shap

print("Testing model & scaler loading...")
model = pickle.load(open("heart_disease_model (3).pkl", "rb"))
scaler = pickle.load(open("scaler (2).pkl", "rb"))
print("Successfully loaded model and scaler!")

feature_names = [
    "Age", "Gender", "Height", "Weight", "Systolic BP", "Diastolic BP", 
    "Cholesterol", "Glucose", "Smoking", "Alcohol", "Physical Activity", 
    "BMI", "Pulse Pressure", "BP Ratio", "BP Sum", "Age*BP", "BMI*Age", 
    "Pulse/BMI", "BP Difference", "Weight/Age", "Height/Weight"
]

# Test sample
age, gender_num, height, weight = 65, 1, 172, 92
bp_hi, bp_lo, chol_num, gluc_num = 155, 95, 3, 2
smoke_num, alco_num, act_num = 1, 1, 0

bmi = weight / ((height/100)**2)
pulse_pressure = bp_hi - bp_lo
bp_ratio = bp_hi / bp_lo
bp_sum = bp_hi + bp_lo
age_bp = age * bp_hi
bmi_age = bmi * age
pulse_bmi = pulse_pressure / bmi
bp_diff = abs(bp_hi - bp_lo)
weight_age = weight / age
height_weight = height / weight

sample = np.array([[
    age, gender_num, height, weight, 
    bp_hi, bp_lo, chol_num, gluc_num, smoke_num, alco_num, 
    act_num, bmi, pulse_pressure, bp_ratio, bp_sum, age_bp, bmi_age, 
    pulse_bmi, bp_diff, weight_age, height_weight
]])

sample_scaled = scaler.transform(sample)
prob = model.predict_proba(sample_scaled)
print(f"Sample prediction probabilities (No Disease vs Disease): {prob[0]}")
print(f"Calculated Risk: {prob[0][1] * 100:.1f}%")

print("Testing SHAP Explainer...")
explainer = shap.TreeExplainer(model)
shap_values = explainer(sample_scaled)
print(f"SHAP explanation generated! Shape: {shap_values.shape}")
explanation = shap_values[0]
if len(explanation.values.shape) == 2:
    exp_vals = explanation.values[:, 1]
    base_val = explanation.base_values[1]
    exp = shap.Explanation(
        values=exp_vals,
        base_values=base_val,
        data=explanation.data,
        feature_names=feature_names
    )
else:
    exp_vals = explanation.values
    base_val = explanation.base_values
    exp = shap.Explanation(
        values=exp_vals,
        base_values=base_val,
        data=explanation.data,
        feature_names=feature_names
    )

print(f"Top impactful features: {sorted(zip(feature_names, exp_vals), key=lambda x: abs(x[1]), reverse=True)[:3]}")

print("Testing SHAP Waterfall Plot generation...")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.5, 3.8))
shap.plots.waterfall(exp, max_display=6, show=False)
plt.tight_layout()
output_fig_path = "test_waterfall.png"
plt.savefig(output_fig_path)
plt.close(fig)
print(f"SHAP Waterfall plot successfully generated and saved to {output_fig_path}!")

print("ALL TESTS PASSED!")

