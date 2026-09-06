import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from styles.theme import render_html
from services.database import fetch_from_mysql, MYSQL_LOADED
from config import PAGES, handle_nav_change

try:
    from streamlit_option_menu import option_menu
    OPTION_MENU_LOADED = True
except ImportError:
    OPTION_MENU_LOADED = False


def render_sidebar(theme: dict):
    """Renders sidebar navigation, EHR dossier logs, and interface preferences."""
    # Guarantees the left sidebar is automatically expanded and never remains hidden
    components.html(
        """
        <script>
        (function() {
            function initSidebarBehavior() {
                try {
                    const pDoc = window.parent.document;
                    if (!pDoc) return;
                    
                    // Direct handler for double right arrows button to expand/return sidebar
                    pDoc.addEventListener('click', function(e) {
                        const expandTrigger = e.target.closest('[data-testid="stExpandSidebarButton"]')
                                           || e.target.closest('[data-testid="stSidebarCollapsedControl"]')
                                           || e.target.closest('button[aria-label="Expand sidebar"]')
                                           || e.target.closest('button[aria-label="Open sidebar"]');
                        if (expandTrigger) {
                            const sidebar = pDoc.querySelector('section[data-testid="stSidebar"]');
                            if (sidebar) {
                                sidebar.setAttribute('aria-expanded', 'true');
                            }
                            if (expandTrigger.tagName !== 'BUTTON') {
                                const innerBtn = expandTrigger.querySelector('button');
                                if (innerBtn) innerBtn.click();
                            }
                        }

                        const collapseTrigger = e.target.closest('[data-testid="stSidebarCollapseButton"]')
                                             || e.target.closest('button[aria-label="Collapse sidebar"]')
                                             || e.target.closest('button[aria-label="Close sidebar"]');
                        if (collapseTrigger) {
                            const sidebar = pDoc.querySelector('section[data-testid="stSidebar"]');
                            if (sidebar) {
                                sidebar.setAttribute('aria-expanded', 'false');
                            }
                        }

                        // On mobile, clicking outside the open drawer automatically closes it
                        if (window.innerWidth <= 768) {
                            const sidebar = pDoc.querySelector('section[data-testid="stSidebar"]');
                            if (sidebar && sidebar.getAttribute('aria-expanded') === 'true') {
                                const insideSidebar = e.target.closest('section[data-testid="stSidebar"]');
                                const isTrigger = e.target.closest('[data-testid="stExpandSidebarButton"]')
                                               || e.target.closest('[data-testid="stSidebarCollapsedControl"]');
                                if (!insideSidebar && !isTrigger) {
                                    sidebar.setAttribute('aria-expanded', 'false');
                                    const closeBtn = pDoc.querySelector('[data-testid="stSidebarCollapseButton"] button')
                                                  || pDoc.querySelector('button[aria-label="Collapse sidebar"]')
                                                  || pDoc.querySelector('button[aria-label="Close sidebar"]');
                                    if (closeBtn) closeBtn.click();
                                }
                            }
                        }
                    }, true);

                } catch(err) {}
            }
            
            initSidebarBehavior();
        })();
        </script>
        """,
        height=0,
        width=0
    )

    card_bg = theme["card_bg"]
    card_border = theme["card_border"]
    glass_shadow = theme["glass_shadow"]
    text_muted = theme["text_muted"]
    primary_blue = theme["primary_blue"]
    primary_light = theme["primary_light"]

    with st.sidebar:
        render_html(f"""
            <div style='background: linear-gradient(135deg, {card_bg} 0%, rgba(255,255,255,0) 100%); 
                        backdrop-filter: blur(20px); border-radius: 20px; padding: 20px 18px; 
                        text-align: center; border: 1px solid {card_border}; 
                        box-shadow: {glass_shadow}; margin-bottom: 18px;'>
                <div style='font-size:32px; margin-bottom:4px;'>🩺</div>
                <h3 style='margin:0; font-size: 1.25rem; font-weight: 800; background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>CardioXAI Suite</h3>
                <p style='margin:4px 0 0 0; font-size: 0.72rem; font-weight: 700; color: {text_muted}; letter-spacing: 1.2px; text-transform: uppercase;'>Precision Cardiology</p>
            </div>
        """)

        if OPTION_MENU_LOADED:
            selected_page = option_menu(
                menu_title=None,
                options=PAGES,
                icons=["bar-chart-fill", "plus-square", "person-badge", "robot", "hospital", "graph-up-arrow"],
                default_index=PAGES.index(st.session_state.current_page) if st.session_state.current_page in PAGES else 0,
                styles={
                    "container":
                     {"padding": "0!important",
                      "background-color": "transparent"},
                    "icon": {"color": primary_blue, "font-size": "17px"},
                    "nav-link":
                     {
                        "font-size": "14px", "text-align": "left", "margin": "4px 0px", "padding": "10px 14px",
                        "font-weight": "600", "color": text_muted, "border-radius": "12px",
                        "transition": "all 0.25s ease"
                    },
                    "nav-link:hover": 
                    {
                        "background-color": primary_light, 
                        "color": primary_blue, "transform": "translateX(4px)"
                    },
                    "nav-link-selected": {
                        "background": f"linear-gradient(135deg, {primary_blue} 0%, #6366f1 100%)",
                        "color": "white", "font-weight": "700", "box-shadow": "0 6px 16px rgba(2, 132, 199, 0.35)",
                    },
                }
            )
            if selected_page != st.session_state.current_page:
                st.session_state.current_page = selected_page
                st.rerun()
        else:
            st.radio(
                "Clinical Navigation", 
                PAGES, 
                index=PAGES.index(st.session_state.current_page) if st.session_state.current_page in PAGES else 0, 
                key="nav_radio", 
                on_change=handle_nav_change, 
                label_visibility="collapsed"
            )

        render_html("<div style='height: 16px;'></div>")

        with st.expander("📁 Patient Dossier Log", expanded=False):
            db_connected = False
            if MYSQL_LOADED and st.session_state.mysql_pwd != "":
                db_df = fetch_from_mysql(st.session_state.mysql_pwd)
                if db_df is not None and not db_df.empty:
                    db_connected = True
                    st.caption("🟢 Connected to MySQL EHR Database")
                    st.dataframe(db_df, hide_index=True, use_container_width=True)

            if not db_connected:
                st.caption("🟡 Local Session Records")
                if len(st.session_state.patient_log) > 0:
                    df_log = pd.DataFrame(st.session_state.patient_log)
                    st.dataframe(df_log[["ID", "Name", "Risk"]], hide_index=True, use_container_width=True)
                    if st.button("🗑️ Clear Local History", use_container_width=True):
                        st.session_state.patient_log = []
                        st.session_state.patient_index = 1
                        st.rerun()
                else:
                    st.info("No patient assessments stored.")

        with st.expander("⚙️ Interface Preferences", expanded=False):
            new_theme = st.toggle("🌙 Dark Mode Theme", value=st.session_state.dark_mode)
            if new_theme != st.session_state.dark_mode:
                st.session_state.dark_mode = new_theme
                st.rerun()
            st.session_state.mysql_pwd = st.text_input(
                "🔑 MySQL DB Password", 
                type="password", 
                value=st.session_state.mysql_pwd, 
                help="Connect local tracker to institutional MySQL server."
            )
