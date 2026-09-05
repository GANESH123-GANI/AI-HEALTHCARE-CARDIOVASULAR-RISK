"""
CardioXAI - AI Clinical Doctor Copilot UI Component
Interactive Clinical Decision Support Chat Interface
"""

import streamlit as st
from services.copilot_service import generate_copilot_response
from styles.theme import render_html


def render_ai_doctor_copilot(pred_results: dict, theme: dict, key_prefix: str = "copilot"):
    """
    Renders an institutional AI Clinical Doctor Copilot chat interface with
    one-click clinical prompt chips, scrollable history, and guideline-backed reasoning.
    """
    st.markdown("#### 🤖 AI Clinical Doctor Copilot")
    st.caption("Real-time Clinical Decision Support (CDSS) for risk stratification, pharmacotherapy, and lifestyle interventions.")

    # 1. Quick-Action Clinical Inquiry Chips (Responsive 2-Tier Layout)
    st.markdown("**⚡ Quick Clinical Prompts:**")
    pending_key = f"{key_prefix}_pending_prompt"

    render_html("<div class='copilot-chips-grid'>")
    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        if st.button("📋 SBAR Note", key=f"{key_prefix}_btn_sbar", use_container_width=True, help="Generate structured SBAR clinical handover note"):
            st.session_state[pending_key] = "Generate SBAR clinical summary"
            st.rerun()
    with qc2:
        if st.button("🩺 BP Protocol", key=f"{key_prefix}_btn_bp", use_container_width=True, help="AHA/ACC Hypertension guidelines & targets"):
            st.session_state[pending_key] = "What is the recommended blood pressure protocol?"
            st.rerun()
    with qc3:
        if st.button("🧪 Statin / Lipids", key=f"{key_prefix}_btn_lipid", use_container_width=True, help="Lipid panel assessment & statin eligibility"):
            st.session_state[pending_key] = "Assess lipid profile and statin recommendation"
            st.rerun()
    with qc4:
        if st.button("🥗 DASH Diet", key=f"{key_prefix}_btn_diet", use_container_width=True, help="DASH diet & sodium restriction protocol"):
            st.session_state[pending_key] = "Provide dietary and DASH recommendations"
            st.rerun()
    render_html("</div>")

    render_html("<div class='copilot-chips-grid' style='margin-top: 4px;'>")
    qc5, qc6, qc7 = st.columns([1, 1, 1])
    with qc5:
        if st.button("⚡ ECG Trace", key=f"{key_prefix}_btn_ecg", use_container_width=True, help="Interpret Lead-II telemetry rhythm"):
            st.session_state[pending_key] = "Interpret the Lead-II ECG telemetry rhythm"
            st.rerun()
    with qc6:
        if st.button("🏃 Zone-2 Rx", key=f"{key_prefix}_btn_ex", use_container_width=True, help="Target heart rate and aerobic exercise plan"):
            st.session_state[pending_key] = "Recommend an exercise and Zone-2 conditioning plan"
            st.rerun()
    with qc7:
        if st.button("🔄 Reset Chat", key=f"{key_prefix}_btn_reset", use_container_width=True, help="Reset conversation history"):
            patient_name = st.session_state.get("patient_name", "Patient")
            st.session_state.chat_history = [
                ("ai", f"Hello Doctor! I am your AI Clinical Copilot. Ask me any question regarding {patient_name}'s risk, blood pressure, BMI, pharmacotherapy, or lifestyle interventions.")
            ]
            st.session_state.pop(pending_key, None)
            st.rerun()
    render_html("</div>")

    # 2. Check for pending quick prompts
    prompt_to_process = None
    if pending_key in st.session_state and st.session_state[pending_key]:
        prompt_to_process = st.session_state.pop(pending_key)

    # 3. Dedicated Chat History Container
    with st.container(height=380, border=True):
        if not st.session_state.get("chat_history"):
            st.session_state.chat_history = [
                ("ai", "Hello Doctor! I am your AI Clinical Copilot. Ask me any question regarding patient risk, blood pressure, BMI, or lifestyle recommendations.")
            ]

        for role, msg in st.session_state.chat_history:
            avatar = "🧑‍⚕️" if role == "user" else "🤖"
            with st.chat_message(role, avatar=avatar):
                st.markdown(msg)

    # 4. User Input Handling
    user_input = st.chat_input(
        "Ask a clinical question (e.g., 'What medication is recommended?', 'Explain heart age')...",
        key=f"{key_prefix}_chat_input"
    )

    active_prompt = prompt_to_process or user_input
    if active_prompt:
        st.session_state.chat_history.append(("user", active_prompt))
        reply = generate_copilot_response(active_prompt, pred_results, st.session_state)
        st.session_state.chat_history.append(("ai", reply))
        st.rerun()
