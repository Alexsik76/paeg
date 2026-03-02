import streamlit as st
from typing import Dict, Any, Tuple, Optional
from core.i18n import t, T


def render_sidebar(config: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    """
    Renders the sidebar for language and lab selection.
    Returns: (selected_language, selected_lab_id)
    """
    # Language Toggle
    lang = st.sidebar.selectbox(
        "Language / Мова", options=["Українська", "English"], index=0
    )

    # Sidebar: Select Lab
    lab_options = {lab["id"]: lab["name"] for lab in config.get("labs", [])}
    selected_lab_id = st.sidebar.selectbox(
        t(T.SELECT_LAB, lang),
        options=list(lab_options.keys()),
        format_func=lambda x: f"{t(T.LAB_PREFIX, lang)} {x}",
    )

    return lang, selected_lab_id