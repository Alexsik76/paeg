import random
from typing import Dict, List

from labs.base import BaseCVK, BaseVoter, BaseScenarioRunner
from labs.lab1.protocol import SimpleVoter
from core.i18n import t, T


def run_simulate_all(
    cvk: BaseCVK, voters: Dict[str, BaseVoter], candidates: List[str], lang: str
) -> List[str]:
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

        payload = active_voter.vote(
            candidate_id=rand_candidate,
            cvk_public_key_pem=cvk.get_public_key(),
            simulate_tampering=False,
        )

        logs.append(t(T.SENDING_PAYLOAD, lang))

        is_success = cvk.process_vote(payload, lang)
        if is_success:
            success_count += 1

        logs.extend(cvk.get_logs())

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
    logs = []
    simulate_tampering = False
    unregistered_str = t(T.UNREGISTERED_USER, lang)

    if selected_voter_id == unregistered_str or scenario_id == "scenario_unregistered":
        active_voter = SimpleVoter(unregistered_str, is_registered=False)
    else:
        active_voter = voters.get(selected_voter_id)

    if not active_voter:
        return [t(T.ERR_UNREGISTERED, lang, voter=selected_voter_id)]

    if scenario_id == "scenario_tampered":
        simulate_tampering = True

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

    if scenario_id == "scenario_double":
        logs.append(t(T.ATTEMPT_1, lang))
        cvk.process_vote(payload, lang)
        logs.extend(cvk.get_logs())

        logs.append(t(T.ATTEMPT_2, lang))
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


class SimpleScenarioRunner(BaseScenarioRunner):
    """
    Scenario runner for Lab 1 (Simple Protocol).
    """

    def __init__(
        self,
        cvk: BaseCVK,
        voters: Dict[str, BaseVoter],
        candidates: List[str],
        lang: str,
    ):
        super().__init__(voters, candidates, lang)
        self.cvk = cvk

    def run(
        self, scenario_id: str, selected_voter_id: str, selected_candidate: str
    ) -> List[str]:
        if scenario_id == "scenario_simulate_all":
            return run_simulate_all(self.cvk, self.voters, self.candidates, self.lang)
        else:
            return run_single_voter_scenario(
                self.cvk,
                self.voters,
                scenario_id,
                selected_voter_id,
                selected_candidate,
                self.lang,
            )
