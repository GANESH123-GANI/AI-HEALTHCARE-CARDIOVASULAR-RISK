import streamlit as st
from styles.theme import render_html
from config import (
    CHOL_OPTIONS, GLUC_OPTIONS, SMOKE_OPTIONS, ALCO_OPTIONS, 
    ACT_OPTIONS, COHORT_PRESETS
)

def render_predict(theme: dict):
    """Renders the Patient Clinical Input & Diagnostic Calibration view (Tab 2)."""
    st.markdown("### 📋 Patient Clinical Input & Diagnostic Calibration")
    st.caption("Adjust clinical parameters below or select a standardized cohort preset to recalculate multi-factor risk.")
    
    # 3-Tier Profile Presets
    render_html("""
        <div class='dossier-card' style='padding: 1.2rem; margin-bottom: 16px;'>
            <div class='kpi-label' style='margin-bottom: 8px;'>⚡ Standardized Cohort Demo Presets</div>
    """)
    render_html("<div class='cohort-presets-grid'>")
    p_col1, p_col2, p_col3 = st.columns(3)
    
    with p_col1:
        if st.button("🔴 Load High-Risk Cohort", use_container_width=True):
            st.session_state.update(COHORT_PRESETS["high_risk"])
            st.toast("Loaded: High-Risk Profile (Robert Martinez, 68M)", icon="🔴")
            st.rerun()
            
    with p_col2:
        if st.button("🟡 Load Borderline Cohort", use_container_width=True):
            st.session_state.update(COHORT_PRESETS["borderline"])
            st.toast("Loaded: Borderline Profile (John Doe, 45M)", icon="🟡")
            st.rerun()
            
    with p_col3:
        if st.button("🟢 Load Optimal Health Cohort", use_container_width=True):
            st.session_state.update(COHORT_PRESETS["optimal"])
            st.toast("Loaded: Optimal Profile (Sarah Jenkins, 32F)", icon="🟢")
            st.rerun()
    render_html("</div>")
    render_html("</div>")

    # Input Form
    render_html("<div class='dossier-card'>")
    st.session_state.patient_name = st.text_input("Patient Full Legal Name", value=st.session_state.patient_name)
    
    tab_in1, tab_in2, tab_in3 = st.tabs(["1️⃣ Demographics & Anthropometrics", "2️⃣ Hemodynamics & Laboratory", "3️⃣ Lifestyle & History"])
    
    with tab_in1:
        render_html("<div class='responsive-two-col'>")
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.age = st.slider("Chronological Age (Years)", 18, 90, int(st.session_state.age))
            st.session_state.gender = st.selectbox("Biological Sex", ["Male", "Female"], index=0 if st.session_state.gender == "Male" else 1)
        with c2:
            st.session_state.height = st.slider("Body Height (cm)", 140, 210, int(st.session_state.height))
            st.session_state.weight = st.slider("Body Weight (kg)", 40, 160, int(st.session_state.weight))
        render_html("</div>")
        
        calc_bmi = st.session_state.weight / ((st.session_state.height/100)**2)
        st.info(f"📊 Calculated Body Mass Index (BMI): **{calc_bmi:.1f} kg/m²**")

    with tab_in2:
        render_html("<div class='responsive-two-col'>")
        c3, c4 = st.columns(2)
        with c3:
            st.session_state.bp_hi = st.slider("Systolic Blood Pressure (mmHg)", 85, 210, int(st.session_state.bp_hi), help="AHA normal range: <120 mmHg.")
            st.session_state.bp_lo = st.slider("Diastolic Blood Pressure (mmHg)", 50, 140, int(st.session_state.bp_lo), help="AHA normal range: <80 mmHg.")
        with c4:
            st.session_state.chol = st.selectbox("Total Serum Cholesterol", CHOL_OPTIONS, index=CHOL_OPTIONS.index(st.session_state.chol))
            st.session_state.gluc = st.selectbox("Fasting Serum Glucose", GLUC_OPTIONS, index=GLUC_OPTIONS.index(st.session_state.gluc))
        render_html("</div>")

    with tab_in3:
        render_html("<div class='responsive-two-col'>")
        c5, c6 = st.columns(2)
        with c5:
            smoke_idx = SMOKE_OPTIONS.index(st.session_state.smoke) if st.session_state.smoke in SMOKE_OPTIONS else (1 if st.session_state.smoke in (True, 1, "Yes") else 0)
            st.session_state.smoke = st.selectbox("🚬 Tobacco Smoking Status", SMOKE_OPTIONS, index=smoke_idx)
            
            alco_idx = ALCO_OPTIONS.index(st.session_state.alco) if st.session_state.alco in ALCO_OPTIONS else (1 if st.session_state.alco in (True, 1, "Yes") else 0)
            st.session_state.alco = st.selectbox("🍷 Alcohol Consumption", ALCO_OPTIONS, index=alco_idx)
        with c6:
            act_idx = ACT_OPTIONS.index(st.session_state.act) if st.session_state.act in ACT_OPTIONS else (1 if st.session_state.act in (True, 1, "Yes") else 0)
            st.session_state.act = st.selectbox("🏃 Physical Activity (≥150 min/wk)", ACT_OPTIONS, index=act_idx)
            
            fam_bool = bool(st.session_state.fam_hist) if not isinstance(st.session_state.fam_hist, str) else st.session_state.fam_hist.lower() in ("yes", "true", "1")
            st.session_state.fam_hist = st.toggle("🧬 Family History of Premature CVD", value=fam_bool)
            if st.session_state.fam_hist:
                st.markdown("<span class='badge-pill badge-crit' style='font-size:0.82rem; font-weight:700; width:100%; justify-content:center;'>⚠️ Genetic CVD Risk Multiplier Active (+15%)</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='badge-pill badge-safe' style='font-size:0.82rem; font-weight:700; width:100%; justify-content:center;'>✅ No Premature CVD Reported in 1st-Degree Relatives</span>", unsafe_allow_html=True)
        render_html("</div>")

    render_html("<div style='height: 20px;'></div>")
    if st.button("🔮 RUN AI DIAGNOSTIC ANALYSIS & GENERATE SHAP INSIGHTS", type="primary", use_container_width=True):
        st.session_state.update({'predicted': True, 'needs_logging': True, 'show_celebration': True, 'current_page': "📊 Dashboard"})
        st.rerun()
    render_html("</div>")
