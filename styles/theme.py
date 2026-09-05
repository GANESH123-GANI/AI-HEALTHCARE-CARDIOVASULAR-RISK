import os
import streamlit as st

# ------------------------------------------------
# HTML RENDERING HELPER (Prevents Markdown Code Blocks)
# ------------------------------------------------
def render_html(html_str: str):
    """
    Renders clean HTML in Streamlit.
    Strips leading/trailing indentation from each line and removes empty lines
    to prevent CommonMark from misinterpreting indented lines as code blocks.
    """
    cleaned = "\n".join([line.strip() for line in html_str.strip().split("\n") if line.strip()])
    st.markdown(cleaned, unsafe_allow_html=True)


# ------------------------------------------------
# THEME TOKENS & COLOR PALETTE
# ------------------------------------------------
def get_theme_tokens(dark_mode: bool = True) -> dict:
    """Returns color tokens and CSS variables according to current theme."""
    accent_purple = "#818cf8"     # Indigo 400
    vibrant_green = "#10b981"     # Emerald 500
    warning_amber = "#f59e0b"     # Amber 500
    muted_red = "#f43f5e"         # Rose 500

    if dark_mode:
        primary_blue = "#38bdf8"          # Bright Sky Blue on dark
        primary_light = "rgba(56, 189, 248, 0.18)"
        primary_btn_bg = "linear-gradient(135deg, #0284c7 0%, #8b5cf6 50%, #d946ef 100%)"
        primary_btn_hover = "linear-gradient(135deg, #38bdf8 0%, #a855f7 50%, #f43f5e 100%)"
        secondary_hover_bg = "rgba(56, 189, 248, 0.2)"
        secondary_hover_text = "#38bdf8"
        secondary_hover_border = "#38bdf8"
        bg_color = "#080d1a"
        bg_gradient = "radial-gradient(ellipse at 50% -10%, #172554 0%, #090d16 65%, #04070f 100%)"
        card_bg = "rgba(15, 23, 42, 0.9)"
        card_sub_bg = "rgba(30, 41, 59, 0.88)"
        card_border = "rgba(255, 255, 255, 0.18)"
        text_main = "#f8fafc"
        text_muted = "#cbd5e1"
        sidebar_bg = "#070b14"
        plotly_template = "plotly_dark"
        glass_shadow = "0 16px 40px -8px rgba(0, 0, 0, 0.75), 0 0 20px rgba(56, 189, 248, 0.15)"
        sb_track = "#090d16"
        sb_thumb = "#1e293b"
        glow_color = "rgba(56, 189, 248, 0.4)"
        badge_safe_color = "#10b981"
        badge_safe_bg = "rgba(16, 185, 129, 0.18)"
        badge_warn_color = "#f59e0b"
        badge_warn_bg = "rgba(245, 158, 11, 0.18)"
        badge_crit_color = "#f43f5e"
        badge_crit_bg = "rgba(244, 63, 94, 0.18)"
    else:
        primary_blue = "#0284c7"          # Deep rich Sky Blue on light
        primary_light = "rgba(2, 132, 199, 0.12)"
        primary_btn_bg = "linear-gradient(135deg, #0284c7 0%, #6366f1 50%, #ec4899 100%)"
        primary_btn_hover = "linear-gradient(135deg, #0369a1 0%, #4f46e5 50%, #db2777 100%)"
        secondary_hover_bg = "rgba(2, 132, 199, 0.16)"
        secondary_hover_text = "#0284c7"
        secondary_hover_border = "#0284c7"
        bg_color = "#f4f7fb"
        bg_gradient = "radial-gradient(ellipse at 50% -10%, #e0e7ff 0%, #f1f5f9 65%, #e2e8f0 100%)"
        card_bg = "#ffffff"
        card_sub_bg = "#f8fafc"
        card_border = "#cbd5e1"
        text_main = "#0f172a"
        text_muted = "#475569"
        sidebar_bg = "#ffffff"
        plotly_template = "plotly_white"
        glass_shadow = "0 12px 30px -6px rgba(100, 116, 139, 0.25), 0 0 16px rgba(2, 132, 199, 0.12)"
        sb_track = "#f1f5f9"
        sb_thumb = "#cbd5e1"
        glow_color = "rgba(2, 132, 199, 0.35)"
        badge_safe_color = "#047857"
        badge_safe_bg = "rgba(16, 185, 129, 0.15)"
        badge_warn_color = "#b45309"
        badge_warn_bg = "rgba(245, 158, 11, 0.15)"
        badge_crit_color = "#be123c"
        badge_crit_bg = "rgba(244, 63, 94, 0.15)"

    return {
        "primary_blue": primary_blue,
        "primary_light": primary_light,
        "primary_btn_bg": primary_btn_bg,
        "primary_btn_hover": primary_btn_hover,
        "secondary_hover_bg": secondary_hover_bg,
        "secondary_hover_text": secondary_hover_text,
        "secondary_hover_border": secondary_hover_border,
        "accent_purple": accent_purple,
        "vibrant_green": vibrant_green,
        "warning_amber": warning_amber,
        "muted_red": muted_red,
        "bg_color": bg_color,
        "bg_gradient": bg_gradient,
        "card_bg": card_bg,
        "card_sub_bg": card_sub_bg,
        "card_border": card_border,
        "text_main": text_main,
        "text_muted": text_muted,
        "sidebar_bg": sidebar_bg,
        "plotly_template": plotly_template,
        "glass_shadow": glass_shadow,
        "sb_track": sb_track,
        "sb_thumb": sb_thumb,
        "glow_color": glow_color,
        "badge_safe_color": badge_safe_color,
        "badge_safe_bg": badge_safe_bg,
        "badge_warn_color": badge_warn_color,
        "badge_warn_bg": badge_warn_bg,
        "badge_crit_color": badge_crit_color,
        "badge_crit_bg": badge_crit_bg,
    }


# ------------------------------------------------
# CSS INJECTION
# ------------------------------------------------
def apply_custom_css(dark_mode: bool = True) -> dict:
    """
    Reads the style.css file, binds CSS root variables based on current theme,
    and injects the stylesheet into Streamlit.
    """
    theme = get_theme_tokens(dark_mode)

    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

    # CSS root custom properties mapped dynamically
    root_vars = f"""
    :root {{
        --bg-color: {theme['bg_color']};
        --bg-gradient: {theme['bg_gradient']};
        --card-bg: {theme['card_bg']};
        --card-sub-bg: {theme['card_sub_bg']};
        --card-border: {theme['card_border']};
        --text-main: {theme['text_main']};
        --text-muted: {theme['text_muted']};
        --sidebar-bg: {theme['sidebar_bg']};
        --glass-shadow: {theme['glass_shadow']};
        --sb-track: {theme['sb-track'] if 'sb-track' in theme else theme['sb_track']};
        --sb-thumb: {theme['sb-thumb'] if 'sb-thumb' in theme else theme['sb_thumb']};
        --primary-blue: {theme['primary_blue']};
        --primary-light: {theme['primary_light']};
        --primary-btn-bg: {theme['primary_btn_bg']};
        --primary-btn-hover: {theme['primary_btn_hover']};
        --secondary-hover-bg: {theme['secondary_hover_bg']};
        --secondary-hover-text: {theme['secondary_hover_text']};
        --secondary-hover-border: {theme['secondary_hover_border']};
        --accent-purple: {theme['accent_purple']};
        --vibrant-green: {theme['vibrant_green']};
        --warning-amber: {theme['warning_amber']};
        --muted-red: {theme['muted_red']};
        --glow-color: {theme['glow_color']};
        --badge-safe-color: {theme['badge_safe_color']};
        --badge-safe-bg: {theme['badge_safe_bg']};
        --badge-warn-color: {theme['badge_warn_color']};
        --badge-warn-bg: {theme['badge_warn_bg']};
        --badge-crit-color: {theme['badge_crit_color']};
        --badge-crit-bg: {theme['badge_crit_bg']};
    }}
    """

    st.markdown(f"<style>{root_vars}\n{css_content}</style>", unsafe_allow_html=True)
    return theme
