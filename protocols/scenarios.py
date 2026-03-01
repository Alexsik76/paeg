"""
Execution scenarios for the voting simulator.
Extracts the complex execution logic out of the main Streamlit UI file.
"""

import random
from typing import Dict, List

from protocols.base import BaseCVK, BaseVoter
from protocols.lab1_simple import SimpleVoter
from core.i18n import t, T


def run_simulate_all(
    cvk: BaseCVK, voters: Dict[str, BaseVoter], candidates: List[str], lang: str
) -> List[str]:
    """
    Simulates a full election where every registered voter casts a vote
    for a random candidate.
    """
    logs = [t(T.SIMULATING_ALL, lang)]
    success_count = 0
    total_count = len(voters)

    for v_id, active_voter in voters.items():
        rand_candidate = random.choice(candidates)
        logs.append(
            t(
                T.VOTER_PREPARING,
                lang,
                voter=active_voter.voter_id,
                candidate=rand_candidate,
            )
        )

        # 1. Voter prepares encrypted ballot
        payload = active_voter.vote(
            candidate_id=rand_candidate,
            cvk_public_key_pem=cvk.get_public_key(),  # Specific to Lab 1 SimpleCVK
            simulate_tampering=False,
        )

        logs.append(t(T.SENDING_PAYLOAD, lang))

        # 2. CVK processes vote
        is_success = cvk.process_vote(payload, lang)
        if is_success:
            success_count += 1

        logs.extend(cvk.get_logs())

    # Final summary log
    if success_count == total_count:
        logs.append(t(T.SIMULATION_OK, lang, count=total_count))
    else:
        logs.append(
            t(
                T.SIMULATION_ERRORS,
                lang,
                success_count=success_count,
                total_count=total_count,
            )
        )

    return logs


def run_single_voter_scenario(
    cvk: BaseCVK,
    voters: Dict[str, BaseVoter],
    scenario_id: str,
    selected_voter_id: str,
    selected_candidate: str,
    lang: str,
) -> List[str]:
    """
    Runs a scenario for a single voter, which can include normal voting,
    unregistered voting, double voting, or a tampered ballot.
    """
    logs = []
    simulate_tampering = False
    unregistered_str = t(T.UNREGISTERED_USER, lang)

    # Determine which voter to simulate
    if selected_voter_id == unregistered_str or scenario_id == "scenario_unregistered":
        active_voter = SimpleVoter(unregistered_str, is_registered=False)
    else:
        active_voter = voters[selected_voter_id]

    if scenario_id == "scenario_tampered":
        simulate_tampering = True

    # Step 1: Voter signs and encrypts ballot
    logs.append(
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

    # Step 2: Execute CVK processing based on scenario rules
    if scenario_id == "scenario_double":
        logs.append(t(T.ATTEMPT_1, lang))
        cvk.process_vote(payload, lang)
        logs.extend(cvk.get_logs())

        logs.append(t(T.ATTEMPT_2, lang))
        # Voter forcefully creates and sends another vote
        payload2 = active_voter.vote(
            candidate_id=selected_candidate,
            cvk_public_key_pem=cvk.get_public_key(),
            simulate_tampering=simulate_tampering,
        )
        cvk.process_vote(payload2, lang)
        logs.extend(cvk.get_logs())
    else:
        logs.append(t(T.SENDING_PAYLOAD, lang))
        cvk.process_vote(payload, lang)
        logs.extend(cvk.get_logs())

    return logs


def execute_scenario(
    scenario_id: str,
    cvk: BaseCVK,
    voters: Dict[str, BaseVoter],
    candidates: List[str],
    selected_voter_id: str,
    selected_candidate: str,
    lang: str,
) -> List[str]:
    """
    Factory runner function to route the execution to the appropriate logic.
    Returns the list of string logs produced during execution.
    """
    if scenario_id == "scenario_simulate_all":
        return run_simulate_all(cvk, voters, candidates, lang)
    else:
        return run_single_voter_scenario(
            cvk, voters, scenario_id, selected_voter_id, selected_candidate, lang
        )
