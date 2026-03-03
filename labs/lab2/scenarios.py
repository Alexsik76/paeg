import random
import uuid
from typing import Dict, List, Mapping, cast

from labs.base import BaseScenarioRunner, BaseVoter
from labs.lab2.protocol import BlindVoter, BlindCVK
from core.i18n import t, T


def run_simulate_all_blind(
    cvk: BlindCVK, voters: Mapping[str, BlindVoter], candidates: List[str], lang: str
) -> List[str]:
    logs = [t(T.SIMULATING_ALL, lang)]
    success_count = 0
    total_count = len(voters)

    cvk_e, cvk_n = cvk.get_public_numbers()
    cvk_pub_pem = cvk.get_public_key()

    for v_id, active_voter in voters.items():
        active_voter.rnd_id = str(random.randint(1000000, 9999999))
        rand_candidate = random.choice(candidates)

        logs.append(
            t(
                T.BLIND_PREPARING_SETS,
                lang,
                voter=v_id,
                voter_rnd_id=active_voter.rnd_id,
            )
        )
        blinded_sets = active_voter.prepare_blinded_sets(cvk_e, cvk_n, candidates)

        logs.append(t(T.BLIND_SENDING_SETS, lang))
        chosen_index, checked_indices = cvk.choose_sets_to_check()

        logs.append(t(T.BLIND_CVK_REQUEST_MULT, lang))
        logs.append(t(T.BLIND_VOTER_SEND_MULT, lang))
        multipliers = active_voter.provide_multipliers(checked_indices)

        signed_set = cvk.verify_and_sign(
            v_id, blinded_sets, checked_indices, multipliers, chosen_index, lang
        )
        logs.extend(cvk.get_logs())

        if signed_set:
            logs.append(t(T.BLIND_UNBLINDING, lang))
            active_voter.process_signed_set(signed_set, chosen_index, cvk_n)

            logs.append(t(T.BLIND_CASTING_VOTE, lang, candidate=rand_candidate))
            payload = active_voter.vote(rand_candidate, cvk_pub_pem)

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


class BlindScenarioRunner(BaseScenarioRunner):
    """
    Scenario runner for Lab 2 (Blind Signature Protocol).
    """

    def __init__(
        self,
        cvk: BlindCVK,
        voters: Dict[str, BlindVoter],
        candidates: List[str],
        lang: str,
    ):
        super().__init__(cast(Dict[str, BaseVoter], voters), candidates, lang)
        self.cvk = cvk

    def run(
        self, scenario_id: str, selected_voter_id: str, selected_candidate: str
    ) -> List[str]:
        if scenario_id == "scenario_simulate_all_blind":
            return run_simulate_all_blind(
                self.cvk,
                cast(Mapping[str, BlindVoter], self.voters),
                self.candidates,
                self.lang,
            )
        else:
            return run_single_voter_scenario_blind(
                self.cvk,
                cast(Mapping[str, BlindVoter], self.voters),
                scenario_id,
                selected_voter_id,
                selected_candidate,
                self.lang,
                self.candidates,
            )


def run_single_voter_scenario_blind(
    cvk: BlindCVK,
    voters: Mapping[str, BlindVoter],
    scenario_id: str,
    selected_voter_id: str,
    selected_candidate: str,
    lang: str,
    candidates: List[str],
) -> List[str]:
    logs = []
    unregistered_str = t(T.UNREGISTERED_USER, lang)

    if selected_voter_id == unregistered_str:
        active_voter = BlindVoter(unregistered_str, is_registered=False)
    else:
        active_voter = voters.get(selected_voter_id)

    if not active_voter:
        return [t(T.ERR_UNREGISTERED, lang, voter=selected_voter_id)]

    cvk_e, cvk_n = cvk.get_public_numbers()
    cvk_pub_pem = cvk.get_public_key()

    active_voter.rnd_id = str(uuid.uuid4())

    def sign_step(tamper=False):
        logs.append(
            t(
                T.BLIND_PREPARING_SETS,
                lang,
                voter=active_voter.voter_id,
                voter_rnd_id=active_voter.rnd_id,
            )
        )
        blinded_sets = active_voter.prepare_blinded_sets(cvk_e, cvk_n, candidates)

        logs.append(t(T.BLIND_SENDING_SETS, lang))
        chosen_index, checked_indices = cvk.choose_sets_to_check()

        logs.append(t(T.BLIND_CVK_REQUEST_MULT, lang))
        logs.append(t(T.BLIND_VOTER_SEND_MULT, lang))

        if tamper:
            active_voter.multipliers[checked_indices[0]][candidates[0]] += 1

        multipliers = active_voter.provide_multipliers(checked_indices)

        signed_set = cvk.verify_and_sign(
            active_voter.voter_id,
            blinded_sets,
            checked_indices,
            multipliers,
            chosen_index,
            lang,
        )
        logs.extend(cvk.get_logs())
        return signed_set, chosen_index

    if scenario_id == "scenario_tamper_blind":
        signed_set, chosen_idx = sign_step(tamper=True)
        return logs

    elif scenario_id == "scenario_double_request_blind":
        logs.append(t(T.ATTEMPT_1, lang))
        signed_set, chosen_idx = sign_step()

        logs.append(t(T.ATTEMPT_2, lang))
        signed_set2, chosen_idx2 = sign_step()
        return logs

    else:
        signed_set, chosen_idx = sign_step()

        if signed_set:
            logs.append(t(T.BLIND_UNBLINDING, lang))
            active_voter.process_signed_set(signed_set, chosen_idx, cvk_n)

            logs.append(t(T.BLIND_CASTING_VOTE, lang, candidate=selected_candidate))
            payload = active_voter.vote(selected_candidate, cvk_pub_pem)

            if cvk.process_vote(payload, lang):
                logs.append(t(T.VOTE_TALLIED, lang, voter=selected_voter_id))
            logs.extend(cvk.get_logs())

            if scenario_id == "scenario_double_vote_blind":
                logs.append(t(T.ATTEMPT_2, lang))
                other_candidates = [c for c in candidates if c != selected_candidate]
                if other_candidates:
                    other_cand = other_candidates[0]
                    logs.append(t(T.BLIND_CAST_SECOND_VOTE, lang))
                    payload2 = active_voter.vote(other_cand, cvk_pub_pem)
                    cvk.process_vote(payload2, lang)
                    logs.extend(cvk.get_logs())

    return logs
