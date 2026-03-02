import streamlit as st
from core.i18n import t, T

# Top-level imports for scenario runners
from labs.lab1.scenarios import SimpleScenarioRunner
from labs.lab2.scenarios import BlindScenarioRunner
from labs.lab3.scenarios import SplitScenarioRunner
from labs.lab4.scenarios import FactorScenarioRunner
from labs.lab5.scenarios import DecentralizedScenarioRunner


def handle_scenario_execution(
    scenario, scenarios, selected_voter_id, selected_candidate, lab_config, lang
):
    """
    Executes the selected voting scenario based on the protocol type.
    Uses unified ScenarioRunner classes for each lab package.
    """
    if scenario is None or selected_voter_id is None or selected_candidate is None:
        st.error(t(T.ERR_SELECT_ALL, lang))
        st.stop()

    st.session_state.logs.append(f"--- {scenarios[scenario]} ---")

    # Common parameters
    voters = st.session_state.voters
    candidates = lab_config.get("settings", {}).get("candidates", [])
    protocol_type = lab_config.get("protocol", "simple")

    # Instantiate the appropriate runner
    runner = None
    match protocol_type:
        case "blind":
            runner = BlindScenarioRunner(st.session_state.cvk, voters, candidates, lang)
        case "split":
            runner = SplitScenarioRunner(
                st.session_state.br, st.session_state.cvk, voters, candidates, lang
            )
        case "factor":
            candidate_ids = lab_config.get("settings", {}).get("candidate_ids", {})
            runner = FactorScenarioRunner(
                st.session_state.vc1,
                st.session_state.vc2,
                st.session_state.cvk,
                voters,
                candidates,
                candidate_ids,
                lang,
            )
        case "decentralized":
            candidate_ids = lab_config.get("settings", {}).get("candidate_ids", {})
            runner = DecentralizedScenarioRunner(
                voters, candidates, candidate_ids, lang
            )
        case _:
            runner = SimpleScenarioRunner(
                st.session_state.cvk, voters, candidates, lang
            )

    # Execute and get logs
    vote_processing_logs = runner.run(scenario, selected_voter_id, selected_candidate)

    # Protocol-specific post-processing
    if protocol_type == "decentralized":
        candidate_ids = lab_config.get("settings", {}).get("candidate_ids", {})
        for cand in candidates:
            count = 0
            for log in vote_processing_logs:
                if t(T.DECENTRALIZED_VOTE_FOUND, lang, cand=cand) in log:
                    count += 1
            st.session_state.cvk.tallies[cand] = count

    # Global conduct check: append logs and show status message
    if vote_processing_logs:
        st.session_state.logs.extend(vote_processing_logs)
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
            last_msg_upper = last_msg.upper()
            is_error = (
                "ERROR" in last_msg_upper
                or "ПОМИЛКА" in last_msg_upper
                or "❌" in last_msg
            )
            is_warning = "WARNING" in last_msg_upper or "ПОПЕРЕДЖЕННЯ" in last_msg_upper

            if is_error:
                st.error(last_msg)
                st.session_state.voting_conducted = False
            elif is_warning:
                st.warning(last_msg)
                st.session_state.voting_conducted = True
            else:
                st.success(last_msg)
                st.session_state.voting_conducted = True
        else:
            st.session_state.voting_conducted = False
