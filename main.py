"""
Main Streamlit Entry Point for Electronic Voting Protocols Simulator.
"""

import streamlit as st

from core.config_parser import load_config, get_lab_config
from labs.lab1.protocol import SimpleCVK, SimpleVoter
from labs.lab2.protocol import BlindCVK, BlindVoter
from labs.lab3.protocol import RegistrationBureau, SplitCVK, SplitVoter
from labs.lab4.protocol import VotingCommission, SplitFactorCVK, SplitFactorVoter
from labs.lab5.protocol import DecentralizedVoter
from labs.lab6.protocol import (
    BlindSplitCVK,
    BlindSplitVoter,
    RegistrationBureau as RB6,
    MiddleLevelCommission,
    LowLevelCommission,
)
from ui.components import render_terminal, render_results, render_tasks
from core.i18n import t, T
from ui.visualizer import SVGProtocolVisualizer


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

if selected_lab_id is None:
    st.stop()

lab_config = get_lab_config(config, selected_lab_id)

st.title(f"{t(T.APP_TITLE, lang)} {t(lab_config['name'], lang)}")


def reset_lab_state():
    """Reset the CVK and voter states for the lab."""
    st.session_state.lab_id = selected_lab_id
    st.session_state.logs = []
    st.session_state.voting_conducted = False

    # Explicitly clear lab-specific components to avoid leakage
    for key in ["br", "vc1", "vc2", "rb", "mcs", "lcs"]:
        if key in st.session_state:
            del st.session_state[key]

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

    elif protocol_type == "decentralized":
        # No CVK in this lab, but we keep a dummy for BaseCVK interface if needed by UI
        st.session_state.cvk = SimpleCVK(candidates=candidates)
        st.session_state.voters = {
            f"voter_{i}": DecentralizedVoter(voter_id=f"voter_{i}")
            for i in range(1, num_voters + 1)
        }
        init_msg = t(T.DECENTRALIZED_INIT, lang)

    elif protocol_type == "lab6_advanced":
        candidate_ids = lab_config.get("settings", {}).get("candidate_ids", {})
        st.session_state.cvk = BlindSplitCVK(
            candidates=candidates, candidate_id_map=candidate_ids
        )
        st.session_state.rb = RB6()
        st.session_state.mcs = [
            MiddleLevelCommission(
                1,
                st.session_state.cvk.crypto_system,
                candidates,
                st.session_state.cvk.id_to_candidate,
            ),
            MiddleLevelCommission(
                2,
                st.session_state.cvk.crypto_system,
                candidates,
                st.session_state.cvk.id_to_candidate,
            ),
        ]
        st.session_state.lcs = [
            LowLevelCommission(1),
            LowLevelCommission(2),
            LowLevelCommission(3),
            LowLevelCommission(4),
        ]
        st.session_state.voters = {
            f"voter_{i}": BlindSplitVoter(voter_id=f"voter_{i}")
            for i in range(1, num_voters + 1)
        }
        init_msg = "ЦВК, Палата реєстрації та комісії ініціалізовані для комбінованого протоколу."

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
tab_names = [
    t(T.CONTROL_PANEL, lang),
    t(T.TERMINAL_LOGS, lang),
    t(T.RESULTS, lang),
]

if str(selected_lab_id) == "6":
    tab_names.append(t(T.SCHEME, lang))

tab_names.append(" " * 5 + "📋 " + t(T.TASKS, lang))

tabs = st.tabs(tab_names)
tab_control = tabs[0]
tab_terminal = tabs[1]
tab_results = tabs[2]

if str(selected_lab_id) == "6":
    tab_scheme = tabs[3]
    tab_tasks = tabs[4]
else:
    tab_tasks = tabs[3]


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
            from ui.scenario_handler import handle_scenario_execution

            handle_scenario_execution(
                scenario,
                scenarios,
                selected_voter_id,
                selected_candidate,
                lab_config,
                lang,
                visualizer=st.session_state.get("visualizer"),
                graph_placeholder=st.session_state.get("graph_placeholder"),
            )

    # New Status Panel directly inside Control Panel
    st.divider()

    voting_conducted = st.session_state.get("voting_conducted", False)

    if voting_conducted:
        st.subheader(t(T.ELECTION_HELD, lang))
    else:
        st.subheader(t(T.ELECTION_NOT_HELD, lang))

    has_logs = len(st.session_state.get("logs", [])) > 0
    if st.button(t(T.RESET_VOTES, lang), disabled=not (voting_conducted or has_logs)):
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


if str(selected_lab_id) == "6":
    with tab_scheme:
        st.subheader(t(T.SCHEME, lang))

        # Stable containers for layout
        controls_container = st.container()
        graph_placeholder = st.empty()

        # Initialize and Render Visualizer at the top to ensure it's in session_state before button press
        from ui.visualizer import SVGProtocolVisualizer

        animation_delay = lab_config.get("settings", {}).get("animation_delay", 1.5)
        if "visualizer" not in st.session_state or not isinstance(
            st.session_state.visualizer, SVGProtocolVisualizer
        ):
            st.session_state.visualizer = SVGProtocolVisualizer(
                duration=animation_delay
            )
        else:
            st.session_state.visualizer.duration = animation_delay

        st.session_state.visualizer.render(graph_placeholder)

        # Quick Controls for the Scheme tab
        with controls_container:
            with st.expander(t(T.VOTE_SETTINGS, lang), expanded=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {t(T.SCENARIO_NORMAL_LAB6, lang)}")
                with col2:
                    # st.write("")  # Padding
                    if st.button(t(T.EXECUTE_SCENARIO, lang), key="scheme_execute"):
                        from ui.scenario_handler import handle_scenario_execution

                        # Use default voter/candidate for the visual scheme
                        voter_id = (
                            list(st.session_state.voters.keys())[0]
                            if st.session_state.voters
                            else "voter_1"
                        )
                        candidate = lab_config.get("settings", {}).get(
                            "candidates", ["Alice (ID 12)"]
                        )[0]

                        handle_scenario_execution(
                            "scenario_normal_lab6",
                            {"scenario_normal_lab6": t(T.SCENARIO_NORMAL_LAB6, lang)},
                            voter_id,
                            candidate,
                            lab_config,
                            lang,
                            visualizer=st.session_state.get("visualizer"),
                            graph_placeholder=graph_placeholder,
                            show_feedback=False,
                        )
                        st.rerun()


with tab_tasks:
    render_tasks(st.session_state.lab_id, lab_config["name"], lang)
