"""
Main Streamlit Entry Point for Electronic Voting Protocols Simulator.
"""

import streamlit as st

from core.config_parser import load_config, get_lab_config
from core.session_manager import reset_lab_state
from ui.sidebar import render_sidebar
from ui.panels import render_control_panel, render_scheme_tab
from ui.components import render_terminal, render_results, render_tasks
from core.i18n import t, T


st.set_page_config(
    page_title="Electronic Voting Simulator",
    page_icon="🗳️",  # Removed the crown icon
    layout="wide",
)

# Hide Streamlit Deploy button
st.markdown(
    """
    <style>
    .stAppDeployButton {display:none;}
    </style>
    """,
    unsafe_allow_html=True,
)



# Load configuration
@st.cache_data
def load_app_config():
    return load_config()


config = load_app_config()

# Render Sidebar
lang, selected_lab_id = render_sidebar(config)

if selected_lab_id is None:
    st.stop()

lab_config = get_lab_config(config, int(selected_lab_id))

st.title(f"{t(T.APP_TITLE, lang)} {t(lab_config['name'], lang)}")


# Initialize or retrieve Session State for the selected Lab
if "lab_id" not in st.session_state or st.session_state.lab_id != selected_lab_id:
    reset_lab_state(lab_config, selected_lab_id, lang)


# Update CVK language on every render (in case it was switched)
st.session_state.cvk.set_language(lang)

# UI Layout: Tabs
tab_names = [
    t(T.CONTROL_PANEL, lang),
    t(T.TERMINAL_LOGS, lang),
    t(T.RESULTS, lang),
]

if str(selected_lab_id) == "6":
    tab_names.append(t(T.SCHEME, lang))

tab_names.append(" " * 5 + "📋 " + t(T.TASKS, lang))

tabs = st.tabs(tab_names)
tab_control, tab_terminal, tab_results = tabs[0], tabs[1], tabs[2]

# ensure `tab_scheme` exists on all code paths so it's never inferred as Unbound
tab_scheme = None
if str(selected_lab_id) == "6":
    tab_scheme = tabs[3]
    tab_tasks = tabs[4]
else:
    tab_tasks = tabs[3]


with tab_control:
    render_control_panel(lab_config, lang, selected_lab_id)

with tab_terminal:
    render_terminal(st.session_state.logs, lang)
    if st.button(t(T.CLEAR_LOGS, lang)):
        st.session_state.logs = []
        st.rerun()

with tab_results:
    render_results(st.session_state.cvk.tallies, lang)


# only enter scheme tab if we actually created one above
if tab_scheme is not None:
    with tab_scheme:
        render_scheme_tab(lab_config, lang)


with tab_tasks:
    render_tasks(st.session_state.lab_id, lab_config["name"], lang)
