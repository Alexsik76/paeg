"""
Main Streamlit Entry Point for Electronic Voting Protocols Simulator.
"""

import streamlit as st

from core.config_parser import load_config, get_lab_config
from labs.lab1.protocol import SimpleCVK, SimpleVoter
from labs.lab2.protocol import BlindCVK, BlindVoter
from labs.lab3.protocol import RegistrationBureau, SplitCVK, SplitVoter
from labs.lab4.protocol import VotingCommission, SplitFactorCVK, SplitFactorVoter
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
    format_func=lambda x: f"{t(T.LAB_PREFIX, lang)} {x}",
)

lab_config = get_lab_config(config, selected_lab_id)

st.title(f"{t(T.APP_TITLE, lang)} {lab_config['name']}")


def reset_lab_state():
    """Reset the CVK and voter states for the lab."""
    st.session_state.lab_id = selected_lab_id
    st.session_state.logs = []
    st.session_state.voting_conducted = False

    protocol_type = lab_config.get("protocol", "simple")
    candidates = lab_config.get("settings", {}).get("candidates", [])
    num_voters = lab_config.get("settings", {}).get("num_voters", 5)

    if protocol_type == "blind":
        st.session_state.cvk = BlindCVK(candidates=candidates)
        st.session_state.voters = {
            f"voter_{i}": BlindVoter(voter_id=f"voter_{i}")
            for i in range(1, num_voters + 1)
        }
        init_msg = t(T.CVK_INIT_BLIND, lang)

    elif protocol_type == "split":
        st.session_state.cvk = SplitCVK(candidates=candidates)
        st.session_state.br = RegistrationBureau()
        st.session_state.voters = {
            f"voter_{i}": SplitVoter(voter_id=f"voter_{i}")
            for i in range(1, num_voters + 1)
        }
        st.session_state.logs.append(t(T.SPLIT_BR_INIT, lang))
        init_msg = t(T.SPLIT_CVK_INIT, lang)

    elif protocol_type == "factor":
        candidate_ids = lab_config.get("settings", {}).get("candidate_ids", {})
        st.session_state.cvk = SplitFactorCVK(
            candidates=candidates, candidate_id_map=candidate_ids
        )
        st.session_state.vc1 = VotingCommission(commission_id=1)
        st.session_state.vc2 = VotingCommission(commission_id=2)
        st.session_state.voters = {
            f"voter_{i}": SplitFactorVoter(voter_id=f"voter_{i}")
            for i in range(1, num_voters + 1)
        }
        init_msg = "ВК-1, ВК-2 та ЦВК ініціалізовані для гомоморфного протоколу."

    else:
        st.session_state.cvk = SimpleCVK(candidates=candidates)
        st.session_state.voters = {
            f"voter_{i}": SimpleVoter(voter_id=f"voter_{i}")
            for i in range(1, num_voters + 1)
        }
        init_msg = t(T.CVK_INIT, lang)

    st.session_state.cvk.set_language(lang)
    st.session_state.logs.append(init_msg)

    # Register all voters by default in CVK
    for voter_id, voter in st.session_state.voters.items():
        st.session_state.cvk.register_voter(
            voter_id, voter.crypto_system.get_public_bytes()
        )

    # Also grab initialization logs
    st.session_state.logs.extend(st.session_state.cvk.get_logs())


# Initialize or retrieve Session State for the selected Lab
if "lab_id" not in st.session_state or st.session_state.lab_id != selected_lab_id:
    reset_lab_state()


# Update CVK language on every render (in case it was switched)
st.session_state.cvk.set_language(lang)

# UI Layout: Tabs
# Added a visual spacer for the Tasks tab to make it stand out
tab_control, tab_terminal, tab_results, tab_tasks = st.tabs(
    [
        t(T.CONTROL_PANEL, lang),
        t(T.TERMINAL_LOGS, lang),
        t(T.RESULTS, lang),
        " " * 5 + "📋 " + t(T.TASKS, lang),
    ]
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

        # Scenario execution logic
        if st.button(t(T.EXECUTE_SCENARIO, lang), type="primary"):
            st.session_state.logs.append(f"--- {scenarios[scenario]} ---")
            cvk: SimpleCVK = st.session_state.cvk

            # Keep track of the number of logs before execution to find the newly added ones
            initial_log_count = len(st.session_state.logs)

            protocol_type = lab_config.get("protocol", "simple")
            if protocol_type == "blind":
                from labs.lab2.scenarios import (
                    run_simulate_all_blind,
                    run_single_voter_scenario_blind,
                )

                if scenario == "scenario_simulate_all_blind":
                    vote_processing_logs = run_simulate_all_blind(
                        cvk, st.session_state.voters, candidates, lang
                    )
                else:
                    vote_processing_logs = run_single_voter_scenario_blind(
                        cvk,
                        st.session_state.voters,
                        scenario,
                        selected_voter_id,
                        selected_candidate,
                        lang,
                        candidates,
                    )
            elif protocol_type == "split":
                from labs.lab3.scenarios import (
                    run_simulate_all_split,
                    run_single_voter_scenario_split,
                )

                if scenario == "scenario_simulate_all_split":
                    vote_processing_logs = run_simulate_all_split(
                        st.session_state.br,
                        cvk,
                        st.session_state.voters,
                        candidates,
                        lang,
                    )
                else:
                    vote_processing_logs = run_single_voter_scenario_split(
                        st.session_state.br,
                        cvk,
                        st.session_state.voters,
                        scenario,
                        selected_voter_id,
                        selected_candidate,
                        lang,
                        candidates,
                    )
            elif protocol_type == "factor":
                from labs.lab4.scenarios import (
                    run_simulate_all_factor,
                    run_single_voter_scenario_factor,
                )

                candidate_ids = lab_config.get("settings", {}).get("candidate_ids", {})

                if scenario == "scenario_simulate_all_factor":
                    vote_processing_logs = run_simulate_all_factor(
                        st.session_state.vc1,
                        st.session_state.vc2,
                        cvk,
                        st.session_state.voters,
                        candidates,
                        candidate_ids,
                        lang,
                    )
                else:
                    vote_processing_logs = run_single_voter_scenario_factor(
                        st.session_state.vc1,
                        st.session_state.vc2,
                        cvk,
                        st.session_state.voters,
                        scenario,
                        selected_voter_id,
                        selected_candidate,
                        candidate_ids,
                        lang,
                    )

            else:
                from labs.lab1.scenarios import (
                    run_simulate_all,
                    run_single_voter_scenario,
                )

                if scenario == "scenario_simulate_all":
                    vote_processing_logs = run_simulate_all(
                        cvk, st.session_state.voters, candidates, lang
                    )
                else:
                    vote_processing_logs = run_single_voter_scenario(
                        cvk,
                        st.session_state.voters,
                        scenario,
                        selected_voter_id,
                        selected_candidate,
                        lang,
                    )

            st.session_state.logs.extend(vote_processing_logs)

            # Show immediate result of the action under the button
            # Filter out empty or separator logs to find the real final status
            meaningful_logs = [
                log_msg
                for log_msg in vote_processing_logs
                if log_msg
                and not log_msg.startswith("---")
                and not log_msg.startswith("Спроба")
                and not log_msg.startswith("Attempt")
            ]
            if meaningful_logs:
                last_msg = meaningful_logs[-1]
                if "ERROR" in last_msg or "ПОМИЛКА" in last_msg:
                    st.error(last_msg)
                elif "WARNING" in last_msg or "ПОПЕРЕДЖЕННЯ" in last_msg:
                    st.warning(last_msg)
                else:
                    st.success(last_msg)

            st.session_state.voting_conducted = True

    # New Status Panel directly inside Control Panel
    st.divider()

    voting_conducted = st.session_state.get("voting_conducted", False)

    if voting_conducted:
        st.subheader(t(T.ELECTION_HELD, lang))
    else:
        st.subheader(t(T.ELECTION_NOT_HELD, lang))

    if st.button(t(T.RESET_VOTES, lang), disabled=not voting_conducted):
        reset_lab_state()
        st.rerun()

    st.write("")
    res_cols = st.columns(len(st.session_state.cvk.tallies))
    for i, (cand, count) in enumerate(st.session_state.cvk.tallies.items()):
        with res_cols[i]:
            st.metric(label=cand, value=count)

    # Check for tie scenario
    if voting_conducted:
        counts = list(st.session_state.cvk.tallies.values())
        if len(counts) > 1 and len(set(counts)) == 1 and counts[0] > 0:
            st.warning(t(T.TIE_WARNING, lang))

with tab_terminal:
    render_terminal(st.session_state.logs, lang)
    if st.button(t(T.CLEAR_LOGS, lang)):
        st.session_state.logs = []
        st.rerun()

with tab_results:
    render_results(st.session_state.cvk.tallies, lang)


with tab_tasks:
    render_tasks(st.session_state.lab_id, lab_config["name"], lang)
