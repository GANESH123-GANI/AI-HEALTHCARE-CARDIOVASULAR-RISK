import os
import pickle
import numpy as np
import streamlit as st
from config import CHOL_DICT, GLUC_DICT, FEATURE_NAMES

MODEL_PATH = "heart_disease_model (3).pkl"
SCALER_PATH = "scaler (2).pkl"

@st.cache_resource
def load_models():
    """Loads and caches the trained Random Forest model and standard scaler."""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        m_path = os.path.join(current_dir, MODEL_PATH) if not os.path.exists(MODEL_PATH) else MODEL_PATH
        s_path = os.path.join(current_dir, SCALER_PATH) if not os.path.exists(SCALER_PATH) else SCALER_PATH

        with open(m_path, "rb") as mf:
            m = pickle.load(mf)
        with open(s_path, "rb") as sf:
            s = pickle.load(sf)
        return m, s
    except Exception as e:
        st.error(f"Error loading model or scaler: {e}")
        return None, None


def is_truthy(val) -> bool:
    """Robust boolean evaluation handling True/False, 1/0, and Yes/No strings."""
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    return str(val).strip().lower() in ("yes", "true", "1", "positive", "y")


def extract_features(state):
    """
    Extracts and engineers the 21 clinical features required by the model.
    Returns:
        raw_data (np.ndarray): Shape (1, 21)
        metrics (dict): Derived intermediate vitals
    """
    weight_val = float(state.weight)
    height_val = float(state.height)
    bmi = weight_val / ((height_val / 100) ** 2) if height_val > 0 else 0.0

    bp_hi = int(state.bp_hi)
    bp_lo = int(state.bp_lo)
    age = int(state.age)
    gender_num = 1 if state.gender == "Male" else 0

    cholesterol_num = CHOL_DICT.get(state.chol, 1)
    glucose_num = GLUC_DICT.get(state.gluc, 1)

    smoking_num = 1 if is_truthy(state.smoke) else 0
    alcohol_num = 1 if is_truthy(state.alco) else 0
    activity_num = 1 if is_truthy(state.act) else 0

    pulse_pressure = bp_hi - bp_lo
    bp_ratio = bp_hi / bp_lo if bp_lo > 0 else 1.0
    bp_sum = bp_hi + bp_lo
    age_bp = age * bp_hi
    bmi_age = bmi * age
    pulse_bmi = pulse_pressure / bmi if bmi > 0 else float(pulse_pressure)
    bp_diff = abs(bp_hi - bp_lo)
    weight_age = weight_val / age if age > 0 else 0.0
    height_weight = height_val / weight_val if weight_val > 0 else height_val

    data = np.array([[
        age, gender_num, height_val, weight_val,
        bp_hi, bp_lo, cholesterol_num, glucose_num, smoking_num, alcohol_num,
        activity_num, bmi, pulse_pressure, bp_ratio, bp_sum, age_bp, bmi_age,
        pulse_bmi, bp_diff, weight_age, height_weight
    ]])

    metrics = {
        "weight_val": weight_val,
        "height_val": height_val,
        "bmi": bmi,
        "bp_hi": bp_hi,
        "bp_lo": bp_lo,
        "age": age,
        "gender_num": gender_num,
        "cholesterol_num": cholesterol_num,
        "glucose_num": glucose_num,
        "smoking_num": smoking_num,
        "alcohol_num": alcohol_num,
        "activity_num": activity_num,
        "pulse_pressure": pulse_pressure,
    }

    return data, metrics


def predict_risk(model, scaler, state):
    """
    Runs ML prediction using the scaled feature vector and applies clinical modifiers.
    Returns:
        dict containing risk, confidence, heart_age, data, data_scaled, metrics, probability
    """
    data, metrics = extract_features(state)

    if model is None or scaler is None:
        return {
            "risk": 0.0,
            "confidence": 0.0,
            "heart_age": metrics["age"],
            "data": data,
            "data_scaled": data,
            "metrics": metrics,
            "probability": np.array([[0.5, 0.5]])
        }

    data_scaled = scaler.transform(data)
    probability = model.predict_proba(data_scaled)
    risk = probability[0][1] * 100.0

    # Clinical risk multipliers
    if is_truthy(state.get("fam_hist", False)):
        risk = min(99.9, risk * 1.15)
    if state.get("aqi", "") == "Poor (High Smog)":
        risk = min(99.9, risk * 1.05)

    confidence = max(probability[0]) * 100.0
    heart_age = int(metrics["age"] + max(0, (risk - 20) / 4))

    # Log assessment to patient history if requested
    if state.get("needs_logging", False):
        state.patient_log.append({
            "ID": f"PT-{state.patient_index:03d}",
            "Name": state.patient_name,
            "Risk": f"{risk:.1f}%",
            "Status": "High Risk" if risk >= 60 else ("Moderate" if risk >= 30 else "Low Risk")
        })
        state.patient_index += 1
        state.needs_logging = False

    return {
        "risk": risk,
        "confidence": confidence,
        "heart_age": heart_age,
        "data": data,
        "data_scaled": data_scaled,
        "metrics": metrics,
        "probability": probability
    }
