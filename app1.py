"""
CardioXAI - Clinical Intelligence Platform
Modularized Streamlit Application Controller (v2.1 Hot-Reload)
"""

import streamlit as st
from config import PAGE_TITLE, PAGE_ICON, init_session_state, calculate_alerts
from styles.theme import apply_custom_css
from services.ml_service import load_models, predict_risk
from components.header import render_header
from components.sidebar import render_sidebar
from components.copilot import render_ai_doctor_copilot
from styles.theme import render_html
from views import (
    render_dashboard,
    render_predict,
    render_action_plan,
    render_doctor_workspace,
    render_analytics
)

# ------------------------------------------------
# 1. PAGE CONFIGURATION
# ------------------------------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------
# 2. STATE & DYNAMIC THEME INJECTION
# ------------------------------------------------
init_session_state()
theme = apply_custom_css(dark_mode=st.session_state.dark_mode)

# ------------------------------------------------
# 3. CLINICAL ML INFERENCE ENGINE
# ------------------------------------------------
model, scaler = load_models()
pred_results = predict_risk(model, scaler, st.session_state)
alert_count = calculate_alerts(st.session_state)

# ------------------------------------------------
# 4. TOP BAR & SIDEBAR NAVIGATION
# ------------------------------------------------
render_header(alert_count=alert_count, theme=theme)
render_sidebar(theme=theme)

# ------------------------------------------------
# 5. CLINICAL ROUTING DISPATCHER
# ------------------------------------------------
current_page = st.session_state.current_page

if current_page == "📊 Dashboard":
    render_dashboard(pred_results=pred_results, theme=theme)
elif current_page == "➕ Predict / Inputs":
    render_predict(theme=theme)
elif current_page == "👤 Patient Action Plan":
    render_action_plan(pred_results=pred_results, model=model, scaler=scaler, theme=theme)
elif current_page == "🤖 AI Clinical Copilot":
    render_html("<div class='dossier-card'>")
    render_ai_doctor_copilot(pred_results=pred_results, theme=theme, key_prefix="sidebar_copilot")
    render_html("</div>")
elif current_page == "🩺 Doctor Workspace":
    render_doctor_workspace(pred_results=pred_results, theme=theme)
elif current_page == "📈 Advanced Analytics":
    render_analytics(pred_results=pred_results, model=model, theme=theme)