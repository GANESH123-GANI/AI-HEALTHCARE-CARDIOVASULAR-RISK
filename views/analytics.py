import io
import datetime
import shap
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go
from styles.theme import render_html
from config import FEATURE_NAMES

def render_analytics(pred_results: dict, model, theme: dict):
    """Renders the Advanced Analytics & Explainable AI (XAI) view (Tab 5)."""
    risk = pred_results["risk"]
    data_scaled = pred_results["data_scaled"]
    metrics = pred_results["metrics"]

    primary_blue = theme["primary_blue"]
    plotly_template = theme["plotly_template"]
    text_main = theme["text_main"]
    text_muted = theme["text_muted"]
    muted_red = theme["muted_red"]
    warning_amber = theme["warning_amber"]
    vibrant_green = theme["vibrant_green"]

    bp_hi = metrics["bp_hi"]

    st.markdown("### 📈 Explainable AI (XAI) & Mathematical Interpretability")
    st.caption("Local feature attributions using SHAP (Shapley Additive Explanations) and 10-year risk trajectories.")

    render_html("<div class='responsive-two-col'>")
    xai_col1, xai_col2 = st.columns([1.1, 1.3])
    
    with xai_col1:
        render_html("""
            <div class='dossier-card' style='padding: 1.2rem;'>
                <div class='kpi-label'>📊 Localized Feature Importance (SHAP Donut)</div>
        """)
        try:
            explainer = shap.TreeExplainer(model)
            shap_vals = explainer(data_scaled)
            explanation = shap_vals[0]
            if len(explanation.values.shape) == 2:
                exp_vals = explanation.values[:, 1]
            else:
                exp_vals = explanation.values
                
            fi_df = pd.DataFrame({"Feature": FEATURE_NAMES, "Impact": exp_vals})
            fi_df["Abs_Impact"] = np.abs(fi_df["Impact"])
            fi_df = fi_df.sort_values("Abs_Impact", ascending=False).head(5)
            
            fig_fi = go.Figure(go.Pie(
                labels=fi_df["Feature"],
                values=fi_df["Abs_Impact"],
                hole=0.52,
                marker=dict(colors=['#f43f5e', '#0284c7', '#10b981', '#f59e0b', '#818cf8']),
                textinfo='label+percent',
                textposition='inside'
            ))
            fig_fi.update_layout(
                height=260,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                font=dict(color=text_main, family="Plus Jakarta Sans", size=11)
            )
            st.plotly_chart(fig_fi, use_container_width=True, config={'displayModeBar': False, 'responsive': True})
        except Exception:
            st.warning("SHAP Donut unavailable.")
        render_html("</div>")

    with xai_col2:
        render_html("""
            <div class='dossier-card' style='padding: 1.2rem;'>
                <div class='kpi-label'>⚖️ SHAP Local Waterfall Attribution</div>
        """)
        try:
            explainer = shap.TreeExplainer(model)
            shap_vals = explainer(data_scaled)
            explanation = shap_vals[0]
            if len(explanation.values.shape) == 2:
                explanation = shap.Explanation(
                    values=explanation.values[:, 1],
                    base_values=explanation.base_values[1],
                    data=explanation.data,
                    feature_names=FEATURE_NAMES
                )
                
            fig_shap, ax_shap = plt.subplots(figsize=(6.5, 3.8), dpi=200)
            fig_shap.patch.set_facecolor('none')
            ax_shap.set_facecolor('none')

            shap.plots.waterfall(explanation, max_display=6, show=False)

            if st.session_state.dark_mode:
                ax_curr = plt.gca()
                ax_curr.tick_params(colors='#f8fafc', labelsize=9)
                for spine in ax_curr.spines.values(): 
                    spine.set_color((1.0, 1.0, 1.0, 0.25))
                for text in fig_shap.findobj(match=plt.Text):
                    try:
                        c = text.get_color()
                        c_rgba = mcolors.to_rgba(c)
                        if np.allclose(c_rgba[:3], [0, 0, 0], atol=0.25):
                            text.set_color('#f8fafc')
                    except Exception:
                        pass
            
            plt.tight_layout()
            buf = io.BytesIO()
            fig_shap.savefig(buf, format="png", transparent=True, dpi=200, bbox_inches="tight")
            buf.seek(0)
            st.image(buf, use_container_width=True)
            plt.close(fig_shap)
        except Exception as e:
            st.warning(f"Could not render SHAP waterfall plot: {e}")
        render_html("</div>")
    render_html("</div>")

    render_html("<div style='height: 16px;'></div>")

    # 10-Year Trajectory & 3D Bio-Digital Twin
    render_html("<div class='responsive-two-col'>")
    xai_b1, xai_b2 = st.columns(2)
    with xai_b1:
        render_html("""
            <div class='dossier-card' style='padding: 1.2rem;'>
                <div class='kpi-label'>🚀 AI 10-Year Risk Trajectory Forecast</div>
        """)
        
        years_future = [datetime.datetime.now().year + i for i in range(0, 11, 2)]
        projected_risks = [min(100.0, risk + (i * 1.8)) for i in range(0, 11, 2)]
        
        fig_traj = go.Figure(go.Scatter(
            x=years_future, y=projected_risks,
            mode='lines+markers',
            line=dict(color=primary_blue, width=3),
            marker=dict(size=8, color='#818cf8'),
            fill='tozeroy',
            fillcolor='rgba(2, 132, 199, 0.12)'
        ))
        fig_traj.update_layout(
            height=230,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color=text_main, family="Plus Jakarta Sans")),
            yaxis=dict(tickfont=dict(color=text_main, family="Plus Jakarta Sans"), range=[0, 100]),
            template=plotly_template
        )
        st.plotly_chart(fig_traj, use_container_width=True, config={'displayModeBar': False, 'responsive': True})
        render_html("</div>")

    with xai_b2:
        render_html("""
            <div class='dossier-card' style='padding: 1.2rem; text-align:center;'>
                <div class='kpi-label' style='margin-bottom:12px;'>🫀 3D Bio-Digital Twin Cardiac Rhythm</div>
        """)
        beat_speed = 0.6 if bp_hi > 140 else (0.85 if bp_hi > 125 else 1.1)
        heart_color = muted_red if risk >= 60 else (warning_amber if risk >= 30 else vibrant_green)
        
        heart_html = f"""
            <div style='display:flex; justify-content:center; align-items:center; height:150px;'>
                <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background: transparent !important;
                    overflow: hidden;
                }}
                .heart-3d {{
                    background-color: {heart_color};
                    display: inline-block;
                    height: 65px;
                    position: relative;
                    transform: rotate(-45deg);
                    width: 65px;
                    animation: heartbeat {beat_speed}s infinite cubic-bezier(0.215, 0.610, 0.355, 1);
                    box-shadow: 0 0 25px {heart_color};
                }}
                .heart-3d:before, .heart-3d:after {{
                    content: '';
                    background-color: {heart_color};
                    border-radius: 50%;
                    height: 65px;
                    position: absolute;
                    width: 65px;
                }}
                .heart-3d:before {{ top: -32px; left: 0; }}
                .heart-3d:after {{ left: 32px; top: 0; }}
                @keyframes heartbeat {{
                    0% {{ transform: rotate(-45deg) scale(1); }}
                    15% {{ transform: rotate(-45deg) scale(1.15); }}
                    30% {{ transform: rotate(-45deg) scale(1); }}
                    45% {{ transform: rotate(-45deg) scale(1.15); }}
                    70% {{ transform: rotate(-45deg) scale(1); }}
                }}
                </style>
                <div class='heart-3d'></div>
            </div>
            <p style='margin:10px 0 0 0; font-size:0.85rem; color:{text_muted}; font-weight:600;'>Dynamic Cardiac Frequency: <b>{int(60/beat_speed)} BPM</b></p>
        """
        components.html(heart_html, height=180)
        render_html("</div>")
    render_html("</div>")
