"""
Main Streamlit Entry Point for Electronic Voting Protocols Simulator.
"""

import streamlit as st
import random

from core.config_parser import load_config, get_lab_config
from protocols.lab1_simple import SimpleCVK, SimpleVoter
from ui.components import render_terminal, render_results
from core.i18n import t, T

st.set_page_config(
    page_title="Electronic Voting Simulator",
    page_icon="🗳️",  # Removed the crown icon
    layout="wide",
)

# Language Toggle
lang = st.sidebar.selectbox(
    "Language / Мова", options=["Українська", "English"], index=0
)


# Load configuration
@st.cache_data
def load_app_config():
    return load_config()


config = load_app_config()

# Sidebar: Select Lab
lab_options = {lab["id"]: lab["name"] for lab in config.get("labs", [])}
selected_lab_id = st.sidebar.selectbox(
    t(T.SELECT_LAB, lang),
    options=list(lab_options.keys()),
    format_func=lambda x: lab_options[x],
)

lab_config = get_lab_config(config, selected_lab_id)

st.title(f"{t(T.APP_TITLE, lang)} {lab_config['name']}")

# Initialize or retrieve Session State for the selected Lab
if "lab_id" not in st.session_state or st.session_state.lab_id != selected_lab_id:
    # Reset state for a new lab
    st.session_state.lab_id = selected_lab_id
    st.session_state.logs = []

    # Setup CVK
    candidates = lab_config.get("settings", {}).get("candidates", [])
    st.session_state.cvk = SimpleCVK(candidates=candidates)
    st.session_state.cvk.set_language(lang)
    st.session_state.logs.append(t(T.CVK_INIT, lang))

    # Setup Voters
    num_voters = lab_config.get("settings", {}).get("num_voters", 5)
    st.session_state.voters = {
        f"voter_{i}": SimpleVoter(voter_id=f"voter_{i}")
        for i in range(1, num_voters + 1)
    }

    # Register all voters by default in CVK
    for voter_id in st.session_state.voters.keys():
        st.session_state.cvk.register_voter(voter_id)

    # Also grab initialization logs
    st.session_state.logs.extend(st.session_state.cvk.get_logs())

# Update CVK language on every render (in case it was switched)
st.session_state.cvk.set_language(lang)

# UI Layout: Tabs
tab_control, tab_terminal, tab_results = st.tabs(
    [t(T.CONTROL_PANEL, lang), t(T.TERMINAL_LOGS, lang), t(T.RESULTS, lang)]
)

with tab_control:
    st.header(t(T.CONTROL_PANEL, lang))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(t(T.VOTE_SETTINGS, lang))
        scenarios = {s["id"]: t(s["id"], lang) for s in lab_config.get("scenarios", [])}
        scenario = st.selectbox(
            t(T.SELECT_SCENARIO, lang),
            options=list(scenarios.keys()),
            format_func=lambda x: scenarios[x],
        )

        candidates = lab_config.get("settings", {}).get("candidates", [])
        selected_candidate = st.selectbox(
            t(T.SELECT_CANDIDATE, lang), options=candidates
        )

        voter_keys = list(st.session_state.voters.keys())
        selected_voter_id = st.selectbox(
            t(T.SELECT_VOTER, lang), options=voter_keys + [t(T.UNREGISTERED_USER, lang)]
        )

    with col2:
        st.subheader(t(T.ACTION, lang))
        if st.button(t(T.EXECUTE_SCENARIO, lang)):
            st.session_state.logs.append(f"--- {scenarios[scenario]} ---")
            cvk: SimpleCVK = st.session_state.cvk

            if scenario == "scenario_simulate_all":
                # Special scenario: 5 voters vote simultaneously for random candidates
                st.session_state.logs.append(t(T.SIMULATING_ALL, lang))
                for v_id, active_voter in st.session_state.voters.items():
                    rand_candidate = random.choice(candidates)
                    st.session_state.logs.append(
                        t(
                            T.VOTER_PREPARING,
                            lang,
                            voter=active_voter.voter_id,
                            candidate=rand_candidate,
                        )
                    )
                    payload = active_voter.vote(
                        candidate_id=rand_candidate,
                        cvk_public_key_pem=cvk.get_public_key(),
                        simulate_tampering=False,
                    )
                    st.session_state.logs.append(t(T.SENDING_PAYLOAD, lang))
                    cvk.process_vote(payload, lang)
                    st.session_state.logs.extend(cvk.get_logs())
            else:
                # Single voter scenarios
                simulate_tampering = False
                unregistered_str = t(T.UNREGISTERED_USER, lang)

                if (
                    selected_voter_id == unregistered_str
                    or scenario == "scenario_unregistered"
                ):
                    active_voter = SimpleVoter(unregistered_str, is_registered=False)
                else:
                    active_voter = st.session_state.voters[selected_voter_id]

                if scenario == "scenario_tampered":
                    simulate_tampering = True

                # 1 & 2: Voter signs and encrypts
                st.session_state.logs.append(
                    t(
                        T.VOTER_PREPARING,
                        lang,
                        voter=active_voter.voter_id,
                        candidate=selected_candidate,
                    )
                )
                payload = active_voter.vote(
                    candidate_id=selected_candidate,
                    cvk_public_key_pem=cvk.get_public_key(),
                    simulate_tampering=simulate_tampering,
                )

                # Additional execution for double voting scenario
                if scenario == "scenario_double":
                    st.session_state.logs.append(t(T.ATTEMPT_1, lang))
                    cvk.process_vote(payload, lang)
                    st.session_state.logs.extend(cvk.get_logs())

                    st.session_state.logs.append(t(T.ATTEMPT_2, lang))
                    # Voter votes again
                    payload2 = active_voter.vote(
                        candidate_id=selected_candidate,
                        cvk_public_key_pem=cvk.get_public_key(),
                        simulate_tampering=simulate_tampering,
                    )
                    cvk.process_vote(payload2, lang)
                    st.session_state.logs.extend(cvk.get_logs())
                else:
                    # 3: CVK processes the single vote
                    st.session_state.logs.append(t(T.SENDING_PAYLOAD, lang))
                    cvk.process_vote(payload, lang)
                    st.session_state.logs.extend(cvk.get_logs())

with tab_terminal:
    render_terminal(st.session_state.logs, lang)
    if st.button(t(T.CLEAR_LOGS, lang)):
        st.session_state.logs = []
        st.rerun()

with tab_results:
    render_results(st.session_state.cvk.tallies, lang)
