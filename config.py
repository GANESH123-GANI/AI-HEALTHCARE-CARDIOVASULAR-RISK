import streamlit as st
import pandas as pd

# ------------------------------------------------
# GLOBAL APPLICATION CONSTANTS
# ------------------------------------------------
PAGE_TITLE = "CardioXAI - Clinical Intelligence Platform"
PAGE_ICON = "🫀"

FEATURE_NAMES = [
    "Age", "Gender", "Height", "Weight", "Systolic BP", "Diastolic BP", 
    "Cholesterol", "Glucose", "Smoking", "Alcohol", "Physical Activity", 
    "BMI", "Pulse Pressure", "BP Ratio", "BP Sum", "Age*BP", "BMI*Age", 
    "Pulse/BMI", "BP Difference", "Weight/Age", "Height/Weight"
]

PAGES = [
    "📊 Dashboard", 
    "➕ Predict / Inputs", 
    "👤 Patient Action Plan", 
    "🤖 AI Clinical Copilot",
    "🩺 Doctor Workspace", 
    "📈 Advanced Analytics"
]

CHOL_OPTIONS = ["Normal", "Above Normal", "Well Above Normal"]
GLUC_OPTIONS = ["Normal", "Above Normal", "Well Above Normal"]
SMOKE_OPTIONS = ["No", "Yes"]
ALCO_OPTIONS = ["No", "Yes"]
ACT_OPTIONS = ["No", "Yes"]
AQI_OPTIONS = ["Good / Normal", "Poor (High Smog)"]

CHOL_DICT = {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}
GLUC_DICT = {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}

# Standardized Cohort Presets
COHORT_PRESETS = {
    "high_risk": {
        'patient_name': 'Robert Martinez', 'age': 68, 'gender': "Male", 
        'height': 172, 'weight': 94, 'bp_hi': 160, 'bp_lo': 96, 
        'chol': "Well Above Normal", 'gluc': "Above Normal", 
        'smoke': "Yes", 'alco': "Yes", 'act': "No", 'fam_hist': True
    },
    "borderline": {
        'patient_name': 'John Doe', 'age': 45, 'gender': "Male", 
        'height': 175, 'weight': 78, 'bp_hi': 135, 'bp_lo': 85, 
        'chol': "Above Normal", 'gluc': "Normal", 
        'smoke': "No", 'alco': "No", 'act': "Yes", 'fam_hist': False
    },
    "optimal": {
        'patient_name': 'Sarah Jenkins', 'age': 32, 'gender': "Female", 
        'height': 165, 'weight': 60, 'bp_hi': 114, 'bp_lo': 74, 
        'chol': "Normal", 'gluc': "Normal", 
        'smoke': "No", 'alco': "No", 'act': "Yes", 'fam_hist': False
    }
}

DEFAULT_PATIENT_VALS = {
    'patient_name': 'John Doe', 
    'age': 45, 
    'height': 175, 
    'weight': 78, 
    'bp_hi': 135, 
    'bp_lo': 85, 
    'gender': "Male",
    'chol': "Above Normal", 
    'gluc': "Normal", 
    'smoke': "No", 
    'alco': "No", 
    'act': "Yes", 
    'fam_hist': False, 
    'aqi': "Good / Normal"
}

# ------------------------------------------------
# SESSION STATE INITIALIZATION
# ------------------------------------------------
def init_session_state():
    """Initializes default Streamlit session state keys if not already set."""
    if "history" not in st.session_state:
        st.session_state.history = pd.DataFrame(columns=["Date", "Risk"])
    if "predicted" not in st.session_state:
        st.session_state.predicted = True
    if "processed_file" not in st.session_state:
        st.session_state.processed_file = None 
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True
    if "current_page" not in st.session_state:
        st.session_state.current_page = PAGES[0]

    # Gamification & Notification State
    if "show_celebration" not in st.session_state:
        st.session_state.show_celebration = False

    # Patient Tracker State
    if "patient_log" not in st.session_state:
        st.session_state.patient_log = [
            {"ID": "PT-001", "Name": "John Doe", "Risk": "34.9%", "Status": "Moderate Risk"}
        ]
    if "patient_index" not in st.session_state:
        st.session_state.patient_index = 2
    if "needs_logging" not in st.session_state:
        st.session_state.needs_logging = False

    # MySQL State
    if "mysql_pwd" not in st.session_state:
        st.session_state.mysql_pwd = ""

    # Chatbot State 
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            ("ai", "Hello! I am your AI Clinical Copilot. Ask me any question regarding patient risk, blood pressure, BMI, or lifestyle recommendations.")
        ]

    for k, v in DEFAULT_PATIENT_VALS.items():
        if k not in st.session_state:
            st.session_state[k] = v

def handle_nav_change():
    """Sync navigation radio change to current page state."""
    st.session_state.current_page = st.session_state.nav_radio

def go_to_predict():
    """Quick jump to the predict / inputs tab."""
    st.session_state.current_page = "➕ Predict / Inputs"

def calculate_alerts(state):
    """Calculates active clinical warning alerts based on patient biomarkers."""
    count = 0
    if state.bp_hi > 130:
        count += 1
    if state.chol in ["Above Normal", "Well Above Normal"]:
        count += 1
    if state.gluc in ["Above Normal", "Well Above Normal"]:
        count += 1
    return count
