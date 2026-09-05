import numpy as np
import pandas as pd
import streamlit as st
from styles.theme import render_html
from components import render_ai_doctor_copilot

def render_doctor_workspace(pred_results: dict, theme: dict):
    """Renders the Institutional Clinical Decision Support System & EHR Workspace (Tab 4)."""
    risk = pred_results["risk"]
    confidence = pred_results["confidence"]
    heart_age = pred_results["heart_age"]
    metrics = pred_results["metrics"]

    card_sub_bg = theme["card_sub_bg"]
    card_border = theme["card_border"]
    text_muted = theme["text_muted"]
    text_main = theme["text_main"]

    bp_hi = metrics["bp_hi"]
    bp_lo = metrics["bp_lo"]
    bmi = metrics["bmi"]
    age = metrics["age"]
    height_val = metrics["height_val"]
    weight_val = metrics["weight_val"]

    # AHA & BMI classification
    if bp_hi < 120 and bp_lo < 80:
        bp_stat = "Normal"
    elif bp_hi <= 129 and bp_lo < 80:
        bp_stat = "Elevated"
    elif bp_hi <= 139 or bp_lo <= 89:
        bp_stat = "Stage 1 HTN"
    else:
        bp_stat = "Stage 2 HTN"

    if bmi < 18.5:
        bmi_stat = "Underweight"
    elif bmi < 25:
        bmi_stat = "Healthy Weight"
    elif bmi < 30:
        bmi_stat = "Overweight"
    else:
        bmi_stat = "Obese"

    st.markdown("### 👨‍⚕️ Institutional Clinical Decision Support System (CDSS)")
    
    doc_tab1, doc_tab2, doc_tab3 = st.tabs([
        "🤖 AI Clinical Doctor Copilot",
        "📑 Clinical EHR Narrative",
        "👥 Multi-Patient Cohort Triage"
    ])
    
    with doc_tab1:
        render_ai_doctor_copilot(pred_results=pred_results, theme=theme, key_prefix="doc_copilot")
        
    with doc_tab2:

        render_html(f"""
            <div class='dossier-card'>
                <div class='kpi-label'>Formal Electronic Health Record (EHR) Medical Note</div>
                <div style='background:{card_sub_bg}; color:{text_main}; padding:18px; border-radius:14px; border:1px solid {card_border}; font-family:monospace; font-size:0.88rem; line-height:1.6;'>
                    <b>SUBJECTIVE:</b><br>
                    Patient {st.session_state.patient_name}, {age}-year-old {st.session_state.gender}, presents for cardiovascular health assessment. Smoking status: {st.session_state.smoke}. Physical activity: {st.session_state.act}. Family history: {"Positive" if st.session_state.fam_hist else "Negative"}.<br><br>
                    <b>OBJECTIVE:</b><br>
                    - Blood Pressure: {bp_hi}/{bp_lo} mmHg ({bp_stat})<br>
                    - Anthropometrics: Height {height_val} cm, Weight {weight_val} kg, BMI {bmi:.1f} kg/m² ({bmi_stat})<br>
                    - Lipid Panel: Serum Cholesterol {st.session_state.chol}<br>
                    - Glycemic Status: Fasting Blood Glucose {st.session_state.gluc}<br><br>
                    <b>ASSESSMENT:</b><br>
                    1. 10-Year Cardiovascular Event Risk: {risk:.1f}% (Model Confidence: {confidence:.1f}%).<br>
                    2. Biological Heart Age: {heart_age} years (+{max(0, heart_age-age)} years biological acceleration).<br>
                    3. Primary Pathogenic Contributors: Elevated Systolic Pressure and Lipids.<br><br>
                    <b>PLAN:</b><br>
                    1. Target BP: <130/80 mmHg via dietary intervention and pharmacotherapy review.<br>
                    2. Dietary Protocol: DASH diet, sodium <2,000 mg/day.<br>
                    3. Re-evaluate in 90 days with repeat lipid panel.
                </div>
            </div>
        """)

    with doc_tab3:
        render_html(f"""
            <div class='dossier-card'>
                <div class='kpi-label'>Multi-Patient Risk & ICU Demand Forecaster</div>
                <p style='color:{text_muted}; font-size:0.86rem;'>Generate a synthetic 50-patient cohort to benchmark hospital resource utilization and ICU triage.</p>
        """)
        
        if st.button("🧬 Generate Synthetic Cohort (50 Patients)", type="primary"):
            np.random.seed(42)
            cohort_df = pd.DataFrame({
                "Patient ID": [f"PT-{i:03d}" for i in range(101, 151)],
                "Age": np.random.randint(35, 78, 50),
                "Gender": np.random.choice(["Male", "Female"], 50),
                "Systolic BP": np.random.randint(110, 175, 50),
                "Diastolic BP": np.random.randint(70, 105, 50),
                "Risk %": np.random.uniform(12.0, 88.0, 50).round(1)
            })
            cohort_df["Triage Tier"] = np.where(
                cohort_df["Risk %"] >= 60, "High Risk", 
                np.where(cohort_df["Risk %"] >= 30, "Moderate", "Low Risk")
            )
            
            crit_count = int((cohort_df["Risk %"] >= 60).sum())
            icu_beds = max(1, int(crit_count * 0.4))
            
            render_html("<div class='cohort-presets-grid'>")
            sc1, sc2, sc3 = st.columns(3)
            with sc1: st.metric("High-Risk Patients", f"{crit_count} / 50")
            with sc2: st.metric("Projected ICU Demand", f"{icu_beds} Beds")
            with sc3: st.metric("Readmission Rate Index", "14.2%")
            render_html("</div>")
            
            st.dataframe(cohort_df, hide_index=True, use_container_width=True)
        render_html("</div>")
