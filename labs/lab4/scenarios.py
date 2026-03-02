import json
import random
import base64
from typing import Dict, List

from labs.base import BaseScenarioRunner
from labs.lab4.protocol import VotingCommission, SplitFactorCVK, SplitFactorVoter
from core.i18n import t, T


def run_simulate_all_factor(
    vc1: VotingCommission,
    vc2: VotingCommission,
    cvk: SplitFactorCVK,
    voters: Dict[str, SplitFactorVoter],
    candidates: List[str],
    candidate_id_map: Dict[str, int],
    lang: str,
) -> List[str]:
    logs = [t(T.SIMULATING_ALL, lang)]
    success_count = 0

    total_count = len(voters)

    key_params = cvk.get_key_params()

    for v_id, active_voter in voters.items():
        rand_name = random.choice(candidates)
        cand_val = candidate_id_map[rand_name]

        # 1. Prepare factors
        p1, p2, f1, f2 = active_voter.vote(cand_val, key_params)
        logs.append(t(T.FACTOR_PREPARING, lang, voter=v_id, val=cand_val, f1=f1, f2=f2))

        # 2. Send to VCs
        logs.append(t(T.FACTOR_SENDING_V1, lang))
        v1_ok = vc1.process_partial_ballot(p1, lang)
        if v1_ok:
            logs.append(t(T.FACTOR_VC_VERIFIED, lang))
        else:
            msg = (
                "Голос відхилено ВК-1 (Дублікат)"
                if lang == "Українська"
                else "Vote rejected by VC-1 (Duplicate)"
            )
            logs.append(f"❌ {msg}")

        logs.append(t(T.FACTOR_SEND_V2, lang))
        v2_ok = vc2.process_partial_ballot(p2, lang)
        if v2_ok:
            logs.append(t(T.FACTOR_VC_VERIFIED, lang))
        else:
            msg = (
                "Голос відхилено ВК-2 (Дублікат)"
                if lang == "Українська"
                else "Vote rejected by VC-2 (Duplicate)"
            )
            logs.append(f"❌ {msg}")

        if v1_ok and v2_ok:
            success_count += 1

    # 3. CVK joins and tallies
    cvk.process_and_tally(vc1.get_partial_ballots(), vc2.get_partial_ballots(), lang)
    logs.extend(cvk.get_logs())

    # Calculate success based on CVK tallies
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


class FactorScenarioRunner(BaseScenarioRunner):
    """
    Scenario runner for Lab 4 (Factor Split Protocol).
    """

    def __init__(
        self,
        vc1: VotingCommission,
        vc2: VotingCommission,
        cvk: SplitFactorCVK,
        voters: Dict[str, SplitFactorVoter],
        candidates: List[str],
        candidate_id_map: Dict[str, int],
        lang: str,
    ):
        super().__init__(voters, candidates, lang)
        self.vc1 = vc1
        self.vc2 = vc2
        self.cvk = cvk
        self.candidate_id_map = candidate_id_map

    def run(
        self, scenario_id: str, selected_voter_id: str, selected_candidate: str
    ) -> List[str]:
        if scenario_id == "scenario_simulate_all_factor":
            return run_simulate_all_factor(
                self.vc1,
                self.vc2,
                self.cvk,
                self.voters,
                self.candidates,
                self.candidate_id_map,
                self.lang,
            )
        else:
            return run_single_voter_scenario_factor(
                self.vc1,
                self.vc2,
                self.cvk,
                self.voters,
                scenario_id,
                selected_voter_id,
                selected_candidate,
                self.candidate_id_map,
                self.lang,
            )


def run_single_voter_scenario_factor(
    vc1: VotingCommission,
    vc2: VotingCommission,
    cvk: SplitFactorCVK,
    voters: Dict[str, SplitFactorVoter],
    scenario_id: str,
    selected_voter_id: str,
    selected_candidate: str,
    candidate_id_map: Dict[str, int],
    lang: str,
) -> List[str]:
    logs = []

    active_voter = voters.get(selected_voter_id)
    if not active_voter:
        return [t(T.ERR_UNREGISTERED, lang, voter=selected_voter_id)]

    cand_val = candidate_id_map[selected_candidate]
    key_params = cvk.get_key_params()

    # 1. Prepare factors
    p1, p2, f1, f2 = active_voter.vote(cand_val, key_params)
    logs.append(
        t(T.FACTOR_PREPARING, lang, voter=selected_voter_id, val=cand_val, f1=f1, f2=f2)
    )

    if scenario_id == "scenario_tamper_factor":
        # Simulate VC-1 tampering by changing the encrypted_factor
        # Let's say VC-1 changes f1 value.

        # Extract original factor
        orig_msg = json.loads(base64.b64decode(p1["message"]).decode("utf-8"))
        orig_val = orig_msg["encrypted_factor"]

        # Tampered val (random multiplier)
        tampered_val = (orig_val * 7) % key_params["n"]

        # 1. Send legitimate factor
        vc1.process_partial_ballot(p1, lang)

        # 2. Tamper it internally
        anon_id = active_voter.anonymous_id
        vc1.partial_ballots[anon_id] = tampered_val
        logs.append(
            "--- [ЗАГРОЗА]: ВК-1 підмінила зашифрований множник для ID виборця ---"
        )

    else:
        # Normal flow
        logs.append(t(T.FACTOR_SENDING_V1, lang))
        if vc1.process_partial_ballot(p1, lang):
            logs.append(t(T.FACTOR_VC_VERIFIED, lang))
        else:
            msg = (
                "Error: Vote rejected by VC-1 (Duplicate or Invalid)."
                if lang == "English"
                else "Помилка: Голос відхилено ВК-1 (Дублікат або невірний підпис)."
            )
            logs.append(f"❌ {msg}")
            return logs

    # VC-2 always receives its factor
    logs.append(t(T.FACTOR_SEND_V2, lang))
    if vc2.process_partial_ballot(p2, lang):
        logs.append(t(T.FACTOR_VC_VERIFIED, lang))
    else:
        msg = (
            "Error: Vote rejected by VC-2 (Duplicate or Invalid)."
            if lang == "English"
            else "Помилка: Голос відхилено ВК-2 (Дублікат або невірний підпис)."
        )
        logs.append(f"❌ {msg}")
        return logs

    # 3. CVK joins and tallies
    cvk.process_and_tally(vc1.get_partial_ballots(), vc2.get_partial_ballots(), lang)
    logs.extend(cvk.get_logs())

    return logs
