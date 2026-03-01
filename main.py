"""
Main Streamlit Entry Point for Electronic Voting Protocols Simulator.
"""

import streamlit as st

from core.config_parser import load_config, get_lab_config
from protocols.lab1_simple import SimpleCVK, SimpleVoter
from ui.components import render_terminal, render_results

st.set_page_config(
    page_title="Electronic Voting Simulator",
    layout="wide",
)


# Load configuration
@st.cache_data
def load_app_config():
    return load_config()


config = load_app_config()

# Sidebar: Select Lab
lab_options = {lab["id"]: lab["name"] for lab in config.get("labs", [])}
selected_lab_id = st.sidebar.selectbox(
    "Select Lab Protocol",
    options=list(lab_options.keys()),
    format_func=lambda x: lab_options[x],
)

lab_config = get_lab_config(config, selected_lab_id)

st.title(f"Simulation: {lab_config['name']}")

# Initialize or retrieve Session State for the selected Lab
if "lab_id" not in st.session_state or st.session_state.lab_id != selected_lab_id:
    # Reset state for a new lab
    st.session_state.lab_id = selected_lab_id
    st.session_state.logs = []

    # Setup CVK
    candidates = lab_config.get("settings", {}).get("candidates", [])
    st.session_state.cvk = SimpleCVK(candidates=candidates)

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

# UI Layout: Tabs
tab_control, tab_terminal, tab_results = st.tabs(
    ["Control Panel", "Terminal Logs", "Results"]
)

with tab_control:
    st.header("Control Panel")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Vote Settings")
        scenarios = {s["id"]: s["name"] for s in lab_config.get("scenarios", [])}
        scenario = st.selectbox(
            "Select Scenario",
            options=list(scenarios.keys()),
            format_func=lambda x: scenarios[x],
        )

        candidates = lab_config.get("settings", {}).get("candidates", [])
        selected_candidate = st.selectbox(
            "Select Candidate to Vote For", options=candidates
        )

        voter_keys = list(st.session_state.voters.keys())
        selected_voter_id = st.selectbox(
            "Select Voter", options=voter_keys + ["unregistered_user"]
        )

    with col2:
        st.subheader("Action")
        if st.button("Execute Scenario"):
            st.session_state.logs.append(
                f"--- Executing Scenario: {scenarios[scenario]} ---"
            )

            # Setup voter based on scenario
            simulate_tampering = False

            if (
                selected_voter_id == "unregistered_user"
                or scenario == "unregistered_voter"
            ):
                # Create a temporary unregistered voter for this scenario
                active_voter = SimpleVoter("unregistered_user", is_registered=False)
            else:
                active_voter = st.session_state.voters[selected_voter_id]

            if scenario == "tampered_ballot":
                simulate_tampering = True

            cvk: SimpleCVK = st.session_state.cvk

            # 1 & 2: Voter signs and encrypts
            st.session_state.logs.append(
                f"Voter {active_voter.voter_id} is preparing ballot for {selected_candidate}..."
            )
            payload = active_voter.vote(
                candidate_id=selected_candidate,
                cvk_public_key_pem=cvk.get_public_key(),
                simulate_tampering=simulate_tampering,
            )

            # Additional execution for double voting scenario
            if scenario == "double_vote":
                st.session_state.logs.append("Attempt 1/2:")
                cvk.process_vote(payload)
                st.session_state.logs.extend(cvk.get_logs())

                st.session_state.logs.append("Attempt 2/2 (Double vote):")
                # Voter votes again
                payload2 = active_voter.vote(
                    candidate_id=selected_candidate,
                    cvk_public_key_pem=cvk.get_public_key(),
                    simulate_tampering=simulate_tampering,
                )
                cvk.process_vote(payload2)
                st.session_state.logs.extend(cvk.get_logs())
            else:
                # 3: CVK processes the vote
                st.session_state.logs.append("Sending encrypted payload to CVK...")
                cvk.process_vote(payload)
                st.session_state.logs.extend(cvk.get_logs())

with tab_terminal:
    render_terminal(st.session_state.logs)
    if st.button("Clear Logs"):
        st.session_state.logs = []
        st.rerun()

with tab_results:
    render_results(st.session_state.cvk.tallies)
