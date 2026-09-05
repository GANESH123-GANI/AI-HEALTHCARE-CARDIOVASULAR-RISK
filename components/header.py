import streamlit as st
from styles.theme import render_html

from config import PAGES

def render_header(alert_count: int, theme: dict):
    """Renders the top clinical header bar, notification popovers, practitioner badge, and navigation tabs."""
    text_muted = theme["text_muted"]
    primary_blue = theme["primary_blue"]
    card_border = theme["card_border"]

    render_html("<div class='header-main-grid'>")
    header_col1, header_col2 = st.columns([2.5, 1.8])
    with header_col1:
        render_html(f"""
            <div style='display:flex; align-items:center; gap:16px;'>
                <div style='width:48px; height:48px; min-width:48px; border-radius:14px; background:linear-gradient(135deg, #0284c7, #818cf8); display:flex; align-items:center; justify-content:center; font-size:24px; box-shadow: 0 4px 14px rgba(2,132,199,0.35);' class='pulse-badge'>🫀</div>
                <div>
                    <h1 style='margin:0; font-size:1.85rem; font-weight:800; letter-spacing:-0.03em;'>CardioXAI Diagnostics</h1>
                    <p style='margin:2px 0 0 0; color:{text_muted}; font-size:0.86rem; font-weight:600;'>Clinical Decision Support System &bull; Random Forest + SHAP Local Attribution</p>
                </div>
            </div>
        """)

    with header_col2:
        render_html("<div class='header-actions-container'>")
        h_act1, h_act2, h_act3 = st.columns([1.1, 1.1, 1.1])
        with h_act1:
            with st.popover(f"🚨 Alerts ({alert_count})", use_container_width=True):
                st.markdown("#### 🔔 Clinical Biomarker Alerts")
                if alert_count == 0:
                    st.success("✅ All vital signs and biomarkers are within reference intervals.")
                else:
                    if st.session_state.bp_hi > 130:
                        st.error(f"⚠️ **Elevated Blood Pressure:** Systolic BP is {st.session_state.bp_hi} mmHg (AHA Stage 1).")
                    if st.session_state.chol in ["Above Normal", "Well Above Normal"]:
                        st.warning(f"⚠️ **Atherogenic Lipids:** Serum cholesterol is '{st.session_state.chol}'.")
                    if st.session_state.gluc in ["Above Normal", "Well Above Normal"]:
                        st.warning(f"⚠️ **Glycemic Alert:** Fasting glucose is '{st.session_state.gluc}'.")
                if st.button("Acknowledge All", use_container_width=True):
                    st.toast("Alerts acknowledged.", icon="✅")
        with h_act2:
            theme_btn_label = "☀️ Light" if st.session_state.dark_mode else "🌙 Dark"
            if st.button(theme_btn_label, key="header_theme_toggle_btn", help="Switch between Dark and Light mode", use_container_width=True):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        with h_act3:
            render_html(f"""
                <div style='display:flex; align-items:center; justify-content:center; height:100%; min-height:38px;'>
                    <span style='background:rgba(56,189,248,0.12); color:{primary_blue}; padding:6px 12px; border-radius:10px; font-weight:700; font-size:0.8rem; white-space:nowrap; border:1px solid rgba(56,189,248,0.25);'>Dr. Lin, MD</span>
                </div>
            """)
        render_html("</div>")
    render_html("</div>")

    render_html(f"<hr style='margin: 10px 0 12px 0; border: none; height: 1px; background: linear-gradient(90deg, {card_border}, transparent);'>")

    # Top Clinical Navigation Tabs Bar (Responsive Grid: 6 cols on desktop, 3x2 on tablet, 2x3 on mobile)
    render_html("<div class='top-nav-container'>")
    nav_cols = st.columns(len(PAGES))
    for i, page_name in enumerate(PAGES):
        with nav_cols[i]:
            is_active = (st.session_state.current_page == page_name)
            btn_type = "primary" if is_active else "secondary"
            if st.button(page_name, key=f"top_nav_bar_{i}", type=btn_type, use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()
    render_html("</div>")

    render_html("<div style='height: 12px;'></div>")
