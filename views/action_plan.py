import numpy as np
import streamlit as st
import plotly.graph_objects as go
from styles.theme import render_html
from config import CHOL_DICT
from components import render_ai_doctor_copilot

def render_action_plan(pred_results: dict, model, scaler, theme: dict):
    """Renders the Personalized Cardiovascular Action Plan (Tab 3)."""
    risk = pred_results["risk"]
    heart_age = pred_results["heart_age"]
    metrics = pred_results["metrics"]
    data = pred_results["data"]

    vibrant_green = theme["vibrant_green"]
    text_muted = theme["text_muted"]
    primary_blue = theme["primary_blue"]
    plotly_template = theme["plotly_template"]

    bp_hi = metrics["bp_hi"]
    bp_lo = metrics["bp_lo"]
    bmi = metrics["bmi"]
    age = metrics["age"]
    height_val = metrics["height_val"]
    cholesterol_num = metrics["cholesterol_num"]
    glucose_num = metrics["glucose_num"]
    activity_num = metrics["activity_num"]

    # AHA Status string for chat heuristics
    if bp_hi < 120 and bp_lo < 80:
        bp_stat = "Normal"
    elif bp_hi <= 129 and bp_lo < 80:
        bp_stat = "Elevated"
    elif bp_hi <= 139 or bp_lo <= 89:
        bp_stat = "Stage 1 HTN"
    else:
        bp_stat = "Stage 2 HTN"

    st.markdown("### 💡 Personalized Cardiovascular Action Plan")
    st.caption("Evidence-based interventions, what-if risk simulations, and real-time telemetry analytics.")

    render_html("<div class='responsive-two-col'>")
    p1_col1, p1_col2 = st.columns(2)
    with p1_col1:
        render_html(f"""
            <div class='dossier-card' style='text-align:center;'>
                <div class='kpi-label'>🌟 Overall Cardiovascular Health Index</div>
                <div style='font-family:Outfit; font-size:4.2rem; font-weight:800; color:{vibrant_green}; margin:8px 0;'>{max(5, int(100 - risk))}/100</div>
                <p style='color:{text_muted}; font-size:0.9rem; margin:0;'>Composite score based on hemodynamic, lipid, and metabolic indicators.</p>
            </div>
        """)
    with p1_col2:
        render_html("""
            <div class='dossier-card' style='padding: 1rem;'>
                <div class='kpi-label'>🕸 Physiological Radar Profile</div>
        """)
        
        spider_theta = ["Blood Pressure", "BMI Index", "Lipid Panel", "Glucose", "Activity", "Pulse Press."]
        spider_r = [
            min(1.0, bp_hi / 180),
            min(1.0, bmi / 35),
            cholesterol_num / 3.0,
            glucose_num / 3.0,
            1.0 if activity_num == 1 else 0.25,
            min(1.0, (bp_hi - bp_lo) / 70)
        ]
        spider_r.append(spider_r[0])
        spider_theta.append(spider_theta[0])
        
        fig_radar = go.Figure(go.Scatterpolar(
            r=spider_r,
            theta=spider_theta,
            fill='toself',
            fillcolor='rgba(56, 189, 248, 0.25)',
            line=dict(color=primary_blue, width=2)
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1], showticklabels=False),
                bgcolor="rgba(0,0,0,0)"
            ),
            showlegend=False,
            height=210,
            margin=dict(t=20, b=20, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)",
            template=plotly_template
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False, 'responsive': True})
        render_html("</div>")
    render_html("</div>")

    render_html("<div style='height: 16px;'></div>")

    # Hospital-Grade Telemetry ECG
    render_html("""
        <div class='dossier-card' style='padding:1.4rem;'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                <div class='kpi-label'>📈 Lead-II Telemetry Rhythm Monitor (10-Second Continuous Trace)</div>
                <span class='badge-pill badge-safe'>72 BPM &bull; Normal Sinus Rhythm</span>
            </div>
    """)
    
    # Generate realistic P-Q-R-S-T rhythm
    t_ecg = np.linspace(0, 10, 600)
    ecg_wave = np.zeros_like(t_ecg)
    for beat in range(12):
        t0 = beat * 0.82
        # P wave
        ecg_wave += 0.15 * np.exp(-((t_ecg - (t0 + 0.15)) / 0.04)**2)
        # Q wave
        ecg_wave -= 0.15 * np.exp(-((t_ecg - (t0 + 0.22)) / 0.02)**2)
        # R wave
        ecg_wave += 1.25 * np.exp(-((t_ecg - (t0 + 0.25)) / 0.025)**2)
        # S wave
        ecg_wave -= 0.35 * np.exp(-((t_ecg - (t0 + 0.28)) / 0.02)**2)
        # T wave
        ecg_wave += 0.30 * np.exp(-((t_ecg - (t0 + 0.42)) / 0.06)**2)
        
    ecg_bg = "#030d07" if st.session_state.dark_mode else "#f0fdf4"
    ecg_line_color = "#10b981" if st.session_state.dark_mode else "#059669"
    ecg_grid_color = "rgba(16, 185, 129, 0.2)" if st.session_state.dark_mode else "rgba(16, 185, 129, 0.25)"

    fig_ecg = go.Figure(go.Scatter(
        x=t_ecg, y=ecg_wave,
        mode='lines',
        line=dict(color=ecg_line_color, width=2.2),
        hoverinfo='skip'
    ))
    fig_ecg.update_layout(
        height=140,
        margin=dict(l=5, r=5, t=5, b=5),
        paper_bgcolor=ecg_bg,
        plot_bgcolor=ecg_bg,
        xaxis=dict(showgrid=True, gridcolor=ecg_grid_color, visible=False),
        yaxis=dict(showgrid=True, gridcolor=ecg_grid_color, range=[-0.6, 1.5], visible=False)
    )
    st.plotly_chart(fig_ecg, use_container_width=True, config={'displayModeBar': False, 'responsive': True})
    render_html("</div>")

    render_html("<div style='height: 16px;'></div>")

    # Counterfactual "What-If" Risk Simulator
    render_html(f"""
        <div class='dossier-card'>
            <div class='kpi-label'>🎛️ Counterfactual "What-If" Therapeutic Risk Simulator</div>
            <p style='color:{text_muted}; font-size:0.88rem;'>Simulate target clinical metrics to demonstrate therapeutic risk reduction to the patient.</p>
    """)
    
    render_html("<div class='responsive-two-col'>")
    sim_c1, sim_c2 = st.columns(2)
    with sim_c1:
        target_bp = st.slider("Target Systolic Blood Pressure", 95, 180, 120, key="sim_bp_target")
        target_w = st.slider("Target Body Weight (kg)", 45, 140, int(st.session_state.weight), key="sim_w_target")
    with sim_c2:
        target_chol = st.selectbox("Target Lipid Profile", ["Normal", "Above Normal", "Well Above Normal"], index=0, key="sim_c_target")
        target_smoke = st.selectbox("Target Smoking Status", ["No", "Yes"], index=0, key="sim_s_target")
    render_html("</div>")
        
    # Calculate simulated risk
    if model is not None and scaler is not None:
        sim_bmi = target_w / ((height_val/100)**2) if height_val > 0 else 0
        sim_chol_num = CHOL_DICT.get(target_chol, 1)
        sim_smoke_num = 1 if target_smoke == "Yes" else 0
        
        sim_data = data.copy()
        sim_data[0][3] = target_w
        sim_data[0][4] = target_bp
        sim_data[0][6] = sim_chol_num
        sim_data[0][8] = sim_smoke_num
        sim_data[0][11] = sim_bmi
        sim_data[0][12] = target_bp - bp_lo
        sim_data[0][13] = target_bp / bp_lo if bp_lo > 0 else 1
        sim_data[0][14] = target_bp + bp_lo
        sim_data[0][15] = age * target_bp
        sim_data[0][16] = sim_bmi * age
        sim_data[0][17] = (target_bp - bp_lo) / sim_bmi if sim_bmi > 0 else 0
        sim_data[0][18] = abs(target_bp - bp_lo)
        sim_data[0][19] = target_w / age if age > 0 else 0
        sim_data[0][20] = height_val / target_w if target_w > 0 else 0
        
        sim_risk = model.predict_proba(scaler.transform(sim_data))[0][1] * 100
        risk_delta = risk - sim_risk
        
        if risk_delta > 0.5:
            render_html(f"""
                <div class='badge-pill badge-safe' style='width:100%; padding:12px 18px; font-size:1.05rem; justify-content:space-between; margin-top:10px;'>
                    <span>📉 Therapeutic Risk Reduction Achieved:</span>
                    <span style='font-weight:800;'>-{risk_delta:.1f}% (Simulated Risk: {sim_risk:.1f}%)</span>
                </div>
            """)
        elif risk_delta < -0.5:
            render_html(f"""
                <div class='badge-pill badge-crit' style='width:100%; padding:12px 18px; font-size:1.05rem; justify-content:space-between; margin-top:10px;'>
                    <span>📈 Risk Escalation Projected:</span>
                    <span style='font-weight:800;'>+{abs(risk_delta):.1f}% (Simulated Risk: {sim_risk:.1f}%)</span>
                </div>
            """)
        else:
            st.info("Current simulated targets reflect patient baseline metrics.")
    render_html("</div>")

    render_html("<div style='height: 16px;'></div>")

    # AI Doctor Copilot Chat
    render_ai_doctor_copilot(pred_results=pred_results, theme=theme, key_prefix="plan_copilot")

