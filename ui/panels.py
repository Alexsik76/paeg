import streamlit as st
from typing import Dict, Any, cast

from core.i18n import t, T
from ui.scenario_handler import handle_scenario_execution
from ui.visualizer import SVGProtocolVisualizer
from core.session_manager import reset_lab_state


def render_control_panel(
    lab_config: Dict[str, Any], lang: str, selected_lab_id: str
) -> None:
    """
    Renders the main control panel with scenario selection and action buttons.
    """
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

    # Status Panel
    st.divider()

    voting_conducted = st.session_state.get("voting_conducted", False)

    if voting_conducted:
        st.subheader(t(T.ELECTION_HELD, lang))
    else:
        st.subheader(t(T.ELECTION_NOT_HELD, lang))

    has_logs = len(st.session_state.get("logs", [])) > 0
    if st.button(t(T.RESET_VOTES, lang), disabled=not (voting_conducted or has_logs)):
        reset_lab_state(lab_config, selected_lab_id, lang)
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


def render_scheme_tab(lab_config: Dict[str, Any], lang: str) -> None:
    """
    Renders the visual scheme tab (Lab 6 specific).
    """
    st.subheader(t(T.SCHEME, lang))

    # Stable containers for layout
    controls_container = cast(Any, st.container())
    graph_placeholder = st.empty()

    # Initialize and Render Visualizer
    animation_delay = lab_config.get("settings", {}).get("animation_delay", 1.5)
    if "visualizer" not in st.session_state or not isinstance(
        st.session_state.visualizer, SVGProtocolVisualizer
    ):
        st.session_state.visualizer = SVGProtocolVisualizer(duration=animation_delay)
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
                if st.button(t(T.EXECUTE_SCENARIO, lang), key="scheme_execute"):
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