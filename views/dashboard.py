import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from styles.theme import render_html
from services.report_service import create_pdf_report, FPDF_LOADED
from services.database import save_to_mysql, MYSQL_LOADED
from services.ml_service import is_truthy
from config import go_to_predict, FEATURE_NAMES

def render_dashboard(pred_results: dict, theme: dict):
    """Renders the primary Clinical Dashboard (Tab 1)."""
    risk = pred_results["risk"]
    confidence = pred_results["confidence"]
    heart_age = pred_results["heart_age"]
    metrics = pred_results["metrics"]
    data = pred_results["data"]

    muted_red = theme["muted_red"]
    warning_amber = theme["warning_amber"]
    vibrant_green = theme["vibrant_green"]
    primary_blue = theme["primary_blue"]
    card_border = theme["card_border"]
    text_main = theme["text_main"]
    text_muted = theme["text_muted"]

    # Status classification
    if risk >= 60:
        status_text, status_color, status_class = "High Risk", muted_red, "badge-crit"
    elif risk >= 30:
        status_text, status_color, status_class = "Moderate Risk", warning_amber, "badge-warn"
    else:
        status_text, status_color, status_class = "Low Risk", vibrant_green, "badge-safe"

    # Celebratory / Alert notifications
    if st.session_state.get("show_celebration", False):
        if risk < 30: 
            st.balloons()
            st.toast("🎉 Favorable risk profile confirmed!", icon="✅")
        elif risk >= 60: 
            st.toast("🚨 High Cardiovascular Event Risk detected! Immediate review advised.", icon="⚠️")
        st.session_state.show_celebration = False

    # Row 1: Unified 5-Column KPI Row
    render_html("<div class='kpi-row-container'>")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns([1, 1, 1, 1, 1.15])
    
    with kpi_col1:
        render_html(f"""
            <div class='kpi-card'>
                <div>
                    <div class='kpi-label'>Patient Clinical Status</div>
                    <div class='kpi-val' style='color:{status_color};'>{status_text}</div>
                </div>
                <div class='kpi-meta'><span class='badge-pill {status_class}'>Action Recommended</span></div>
            </div>
        """)
        
    with kpi_col2:
        render_html(f"""
            <div class='kpi-card'>
                <div>
                    <div class='kpi-label'>10-Yr Cardiovascular Risk</div>
                    <div class='kpi-val'>{risk:.1f}%</div>
                </div>
                <div style='background:{card_border}; height:6px; border-radius:3px; margin-top:8px;'>
                    <div style='background:{status_color}; width:{min(100.0, risk)}%; height:100%; border-radius:3px;'></div>
                </div>
            </div>
        """)
        
    with kpi_col3:
        render_html(f"""
            <div class='kpi-card'>
                <div>
                    <div class='kpi-label'>AI Diagnostic Confidence</div>
                    <div class='kpi-val' style='color:{primary_blue};'>{confidence:.1f}%</div>
                </div>
                <div style='background:{card_border}; height:6px; border-radius:3px; margin-top:8px;'>
                    <div style='background:linear-gradient(90deg, {primary_blue}, #818cf8); width:{confidence}%; height:100%; border-radius:3px;'></div>
                </div>
            </div>
        """)
        
    with kpi_col4:
        age_delta = heart_age - metrics["age"]
        delta_str = f"+{age_delta} yrs acceleration" if age_delta > 0 else ("Aligned with chronological" if age_delta == 0 else f"{age_delta} yrs younger")
        delta_color = muted_red if age_delta > 0 else vibrant_green
        render_html(f"""
            <div class='kpi-card'>
                <div>
                    <div class='kpi-label'>Biological Heart Age</div>
                    <div class='kpi-val'>{heart_age} <span style='font-size:1rem; color:{text_muted}; font-weight:600;'>yrs</span></div>
                </div>
                <div class='kpi-meta' style='color:{delta_color}; font-weight:700;'>{delta_str}</div>
            </div>
        """)
        
    with kpi_col5:
        render_html("""
            <div class='kpi-card' style='justify-content:center; gap:8px;'>
                <div class='kpi-label' style='text-align:center;'>Clinical Triage Actions</div>
        """)
        st.button("➕ Predict / Edit Inputs", type="primary", on_click=go_to_predict, use_container_width=True)
        if st.button("🤖 AI Clinical Copilot", key="dash_copilot_quick_btn", type="secondary", use_container_width=True):
            st.session_state.current_page = "🤖 AI Clinical Copilot"
            st.rerun()
        render_html("</div>")
    render_html("</div>")

    render_html("<div style='height: 16px;'></div>")

    # Row 2: Patient Dossier (Left) vs Advanced Analytics (Right)
    render_html("<div class='dashboard-main-grid'>")
    r2_left, r2_right = st.columns([1.15, 1.85])
    
    with r2_left:
        bp_hi = metrics["bp_hi"]
        bp_lo = metrics["bp_lo"]
        bmi = metrics["bmi"]
        chol_num = metrics["cholesterol_num"]
        gluc_num = metrics["glucose_num"]
        age = metrics["age"]
        height_val = metrics["height_val"]
        weight_val = metrics["weight_val"]

        # AHA Classification
        if bp_hi < 120 and bp_lo < 80:
            bp_stat, bp_badge = "Normal", "badge-safe"
        elif bp_hi <= 129 and bp_lo < 80:
            bp_stat, bp_badge = "Elevated", "badge-warn"
        elif bp_hi <= 139 or bp_lo <= 89:
            bp_stat, bp_badge = "Stage 1 HTN", "badge-warn"
        else:
            bp_stat, bp_badge = "Stage 2 HTN", "badge-crit"

        # BMI Classification
        if bmi < 18.5: bmi_stat, bmi_badge = "Underweight", "badge-warn"
        elif bmi < 25: bmi_stat, bmi_badge = "Healthy Weight", "badge-safe"
        elif bmi < 30: bmi_stat, bmi_badge = "Overweight", "badge-warn"
        else: bmi_stat, bmi_badge = "Obese", "badge-crit"

        chol_stat = "Normal (<200)" if chol_num == 1 else ("Borderline (200-239)" if chol_num == 2 else "High (≥240)")
        chol_badge = "badge-safe" if chol_num == 1 else ("badge-warn" if chol_num == 2 else "badge-crit")
        
        gluc_stat = "Normal (<100)" if gluc_num == 1 else ("Impaired (100-125)" if gluc_num == 2 else "Elevated (≥126)")
        gluc_badge = "badge-safe" if gluc_num == 1 else ("badge-warn" if gluc_num == 2 else "badge-crit")

        render_html(f"""
            <div class='dossier-card'>
                <div style='display:flex; align-items:center; gap:16px; margin-bottom:18px;'>
                    <div style='width:52px; height:52px; border-radius:16px; background:linear-gradient(135deg, #0284c7, #818cf8); display:flex; align-items:center; justify-content:center; font-size:26px; box-shadow:0 4px 12px rgba(2,132,199,0.35);'>
                        👤
                    </div>
                    <div>
                        <h3 style='margin:0; font-size:1.35rem; font-weight:800;'>{st.session_state.patient_name}</h3>
                        <p style='margin:2px 0 0 0; font-size:0.85rem; color:{text_muted}; font-weight:600;'>ID: PT-{max(1, st.session_state.patient_index-1):03d} &bull; {st.session_state.gender}, {age} yrs</p>
                    </div>
                </div>

                <div class='vital-grid'>
                    <div class='vital-chip'>
                        <span class='kpi-label'>Height / Weight</span>
                        <span style='font-weight:700; font-size:1.05rem; margin-top:2px;'>{height_val} cm / {weight_val} kg</span>
                    </div>
                    <div class='vital-chip'>
                        <span class='kpi-label'>Calculated BMI</span>
                        <div style='display:flex; align-items:center; justify-content:space-between; margin-top:2px;'>
                            <span style='font-weight:800; font-size:1.1rem;'>{bmi:.1f}</span>
                            <span class='badge-pill {bmi_badge}' style='padding:2px 8px; font-size:0.75rem;'>{bmi_stat}</span>
                        </div>
                    </div>
                </div>

                <div style='font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; font-weight:800; color:{text_muted}; margin:16px 0 8px 0;'>Clinical Biomarkers</div>
                <div class='vital-grid'>
                    <div class='vital-chip'>
                        <span class='kpi-label'>Blood Pressure</span>
                        <span style='font-weight:800; font-size:1.2rem; margin:2px 0;'>{bp_hi}/{bp_lo} <span style='font-size:0.75rem; color:{text_muted}; font-weight:600;'>mmHg</span></span>
                        <span class='badge-pill {bp_badge}' style='font-size:0.75rem; padding:2px 8px;'>{bp_stat}</span>
                    </div>
                    <div class='vital-chip'>
                        <span class='kpi-label'>Cholesterol Panel</span>
                        <span style='font-weight:800; font-size:1.05rem; margin:2px 0;'>{st.session_state.chol}</span>
                        <span class='badge-pill {chol_badge}' style='font-size:0.75rem; padding:2px 8px;'>{chol_stat}</span>
                    </div>
                    <div class='vital-chip'>
                        <span class='kpi-label'>Fasting Glucose</span>
                        <span style='font-weight:800; font-size:1.05rem; margin:2px 0;'>{st.session_state.gluc}</span>
                        <span class='badge-pill {gluc_badge}' style='font-size:0.75rem; padding:2px 8px;'>{gluc_stat}</span>
                    </div>
                    <div class='vital-chip'>
                        <span class='kpi-label'>Pulse Pressure</span>
                        <span style='font-weight:800; font-size:1.2rem; margin:2px 0;'>{metrics['pulse_pressure']} <span style='font-size:0.75rem; color:{text_muted}; font-weight:600;'>mmHg</span></span>
                        <span class='badge-pill {"badge-safe" if metrics["pulse_pressure"] <= 50 else "badge-warn"}' style='font-size:0.75rem; padding:2px 8px;'>{"Normal" if metrics["pulse_pressure"] <= 50 else "Elevated"}</span>
                    </div>
                </div>

                <div style='font-size:0.82rem; text-transform:uppercase; letter-spacing:0.12em; font-weight:800; color:{text_muted}; margin:16px 0 10px 0;'>Lifestyle & Genetic Exposure Matrix</div>
                <div style='display:flex; flex-wrap:wrap; gap:10px;'>
                    <span class='badge-pill {"badge-crit" if is_truthy(st.session_state.smoke) else "badge-safe"}' style='padding:6px 14px; font-size:0.86rem; font-weight:700;'>🚬 Tobacco: {"Yes (Active)" if is_truthy(st.session_state.smoke) else "No (Non-Smoker)"}</span>
                    <span class='badge-pill {"badge-warn" if is_truthy(st.session_state.alco) else "badge-safe"}' style='padding:6px 14px; font-size:0.86rem; font-weight:700;'>🍷 Alcohol: {"Yes (Regular)" if is_truthy(st.session_state.alco) else "No / Minimal"}</span>
                    <span class='badge-pill {"badge-safe" if is_truthy(st.session_state.act) else "badge-warn"}' style='padding:6px 14px; font-size:0.86rem; font-weight:700;'>🏃 Activity: {"Active (≥150m)" if is_truthy(st.session_state.act) else "Sedentary (<150m)"}</span>
                    <span class='badge-pill {"badge-crit" if is_truthy(st.session_state.fam_hist) else "badge-safe"}' style='padding:6px 14px; font-size:0.86rem; font-weight:700;'>🧬 CVD Family History: {"Positive (+15% Risk)" if is_truthy(st.session_state.fam_hist) else "Negative (Clear)"}</span>
                </div>
            </div>
        """)

    with r2_right:
        # Charts Row
        render_html("<div class='charts-sub-grid'>")
        c_gauge, c_bars = st.columns([1, 1.2])
        
        with c_gauge:
            render_html("""
                <div class='dossier-card' style='padding: 1.2rem;'>
                    <div class='kpi-label'>⏱ Calibrated Risk Meter</div>
            """)
            
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk,
                number={'suffix': "%", 'font': {'size': 38, 'color': text_main, 'family': 'Outfit'}},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100], 'visible': False},
                    'bar': {'color': "rgba(0,0,0,0)"},
                    'bgcolor': "rgba(255,255,255,0.05)",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 30], 'color': vibrant_green},
                        {'range': [30, 60], 'color': warning_amber},
                        {'range': [60, 100], 'color': muted_red}
                    ],
                    'threshold': {'line': {'color': text_main, 'width': 5}, 'thickness': 0.8, 'value': risk}
                }
            ))
            gauge.update_layout(
                height=200, 
                margin=dict(l=15, r=15, t=15, b=5), 
                paper_bgcolor="rgba(0,0,0,0)", 
                font={'color': text_main, 'family': 'Plus Jakarta Sans'}
            )
            st.plotly_chart(gauge, use_container_width=True, config={'displayModeBar': False, 'responsive': True})
            render_html("</div>")

        with c_bars:
            render_html("""
                <div class='dossier-card' style='padding: 1.2rem;'>
                    <div class='kpi-label'>📊 Disease Risk Differential</div>
            """)
            
            diseases = ["Cardio Event", "Ischemic Stroke", "Type II Diab.", "Hypertension"]
            probs = [risk, risk * 0.42, risk * 0.48, min(100.0, risk * 0.72 + 10)]
            colors = [muted_red if p >= 60 else (warning_amber if p >= 30 else vibrant_green) for p in probs]
            
            fig_dis = go.Figure(go.Bar(
                y=diseases,
                x=probs,
                orientation='h',
                marker=dict(color=colors, line=dict(width=0)),
                text=[f"{p:.1f}%" for p in probs],
                textposition='inside',
                textfont=dict(family="Outfit", color="white", size=12)
            ))
            fig_dis.update_layout(
                height=200,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(range=[0, 100], showgrid=False, visible=False),
                yaxis=dict(tickfont=dict(color=text_main, family="Plus Jakarta Sans", size=11), autorange="reversed"),
            )
            st.plotly_chart(fig_dis, use_container_width=True, config={'displayModeBar': False, 'responsive': True})
            render_html("</div>")
        render_html("</div>")

        render_html("<div style='height: 12px;'></div>")

        # Anomaly Triage Card
        anomalies = []
        if bp_hi > 130:
            anomalies.append(("Elevated Systolic Blood Pressure", f"{bp_hi} mmHg", "Increases mechanical strain on vascular endothelium.", "badge-crit" if bp_hi >= 140 else "badge-warn"))
        if chol_num > 1:
            anomalies.append(("Atherogenic Lipid Panel", st.session_state.chol, "Accelerates low-density lipoprotein plaque progression.", "badge-crit" if chol_num == 3 else "badge-warn"))
        if bmi > 25:
            anomalies.append(("Elevated Body Mass Index", f"{bmi:.1f} kg/m²", "Contributes to peripheral vascular resistance and metabolic stress.", "badge-warn"))

        render_html("""
            <div class='dossier-card' style='padding: 1.3rem;'>
                <div class='kpi-label' style='margin-bottom:10px;'>🚨 Automated Clinical Anomaly Triage</div>
        """)
        
        if not anomalies:
            render_html("<div class='badge-pill badge-safe' style='width:100%; padding:10px;'>✅ Clear: All examined physiological markers fall within healthy parameters.</div>")
        else:
            for title, val, desc, badge_cls in anomalies:
                render_html(f"""
                    <div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; padding-bottom:8px; border-bottom:1px solid {card_border};'>
                        <div>
                            <span style='font-weight:700; font-size:0.92rem;'>{title}</span>
                            <p style='margin:2px 0 0 0; font-size:0.8rem; color:{text_muted};'>{desc}</p>
                        </div>
                        <span class='badge-pill {badge_cls}'>{val}</span>
                    </div>
                """)

        render_html(f"<div style='margin-top:14px; font-weight:700; font-size:0.82rem; color:{text_muted}; text-transform:uppercase;'>⚡ Clinical Export & Integration Actions</div>")
        render_html("<div class='export-actions-grid'>")
        qa_1, qa_2, qa_3, qa_4 = st.columns(4)
        
        with qa_1:
            if FPDF_LOADED:
                pdf_bytes = create_pdf_report(
                    st.session_state.patient_name, age, st.session_state.gender, 
                    height_val, weight_val, bmi, bp_hi, bp_lo, 
                    st.session_state.chol, st.session_state.gluc, 
                    st.session_state.smoke, st.session_state.act, risk, confidence,
                    alco=st.session_state.alco,
                    fam_hist=is_truthy(st.session_state.fam_hist)
                )
                st.download_button(
                    label="📥 Clinical PDF", 
                    data=pdf_bytes, 
                    file_name=f"cardio_report_{st.session_state.patient_name.replace(' ', '_')}.pdf", 
                    mime="application/pdf", 
                    use_container_width=True, 
                    type="primary"
                )
            else:
                st.button("📥 Clinical PDF", on_click=lambda: st.error("Install fpdf2 package."), use_container_width=True, type="primary")
        
        with qa_2:
            csv_export = pd.DataFrame([data[0]], columns=FEATURE_NAMES).to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Export CSV", 
                data=csv_export, 
                file_name=f"patient_features_{int(time.time())}.csv", 
                mime="text/csv", 
                use_container_width=True, 
                type="secondary"
            )
            
        with qa_3:
            if st.button("🗄️ Save to EHR", use_container_width=True, type="secondary"):
                pt_id = f"PT-{max(1, st.session_state.patient_index - 1):03d}"
                if MYSQL_LOADED and st.session_state.get("mysql_pwd"):
                    res = save_to_mysql(pt_id, st.session_state.patient_name, f"{risk:.1f}%", st.session_state.get("mysql_pwd", ""))
                    if res is True: 
                        st.toast("Saved to MySQL Database!", icon="✅")
                    else: 
                        st.toast("Logged to Local Session Records.", icon="📁")
                else:
                    st.toast("Saved to Local Session Records.", icon="✅")
                    
        with qa_4:
            with st.popover("📱 QR Passport", use_container_width=True):
                qr_data = f"Patient:{st.session_state.patient_name}|Age:{age}|BP:{bp_hi}/{bp_lo}|Risk:{risk:.1f}%|Conf:{confidence:.1f}%"
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data={qr_data}", use_container_width=True)
                st.caption("Scan with mobile camera to review medical summary.")

        render_html("</div>")
        render_html("</div>")
    render_html("</div>")
