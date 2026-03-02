import random
import uuid
from typing import Dict, List
from labs.base import BaseScenarioRunner
from labs.lab3.protocol import RegistrationBureau, SplitCVK, SplitVoter
from core.i18n import t, T


def run_simulate_all_split(
    br: RegistrationBureau,
    cvk: SplitCVK,
    voters: Dict[str, SplitVoter],
    candidates: List[str],
    lang: str,
) -> List[str]:
    logs = [t(T.SPLIT_SIMULATING_ALL, lang)]
    success_count = 0
    total_count = len(voters)

    cvk_pub_pem = cvk.get_public_key()

    for v_id, active_voter in voters.items():
        rand_candidate = random.choice(candidates)
        logs.append(t(T.SPLIT_VOTER_REQUESTS_RN, lang, voter=v_id))

        # Voter requests RN
        rn = br.register_voter(v_id, lang)
        if not rn:
            logs.append(t(T.SPLIT_ERR_DOUBLE_RN, lang, voter=v_id))
            continue

        logs.append(t(T.SPLIT_BR_ISSUED_RN, lang, voter=v_id))
        active_voter.set_rn(rn)

        # Send updated valid RNs to CVK (representing BR doing its job in the background)
        cvk.load_rns_from_br(br.get_valid_rns())

        # Voter creates ballot
        logs.append(t(T.SPLIT_VOTER_VOTING, lang, voter=v_id))
        payload = active_voter.vote(rand_candidate, cvk_pub_pem)

        # CVK processes
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


class SplitScenarioRunner(BaseScenarioRunner):
    """
    Scenario runner for Lab 3 (Split Protocol).
    """

    def __init__(
        self,
        br: RegistrationBureau,
        cvk: SplitCVK,
        voters: Dict[str, SplitVoter],
        candidates: List[str],
        lang: str,
    ):
        super().__init__(voters, candidates, lang)
        self.br = br
        self.cvk = cvk

    def run(
        self, scenario_id: str, selected_voter_id: str, selected_candidate: str
    ) -> List[str]:
        if scenario_id == "scenario_simulate_all_split":
            return run_simulate_all_split(
                self.br, self.cvk, self.voters, self.candidates, self.lang
            )
        else:
            return run_single_voter_scenario_split(
                self.br,
                self.cvk,
                self.voters,
                scenario_id,
                selected_voter_id,
                selected_candidate,
                self.lang,
                self.candidates,
            )


def run_single_voter_scenario_split(
    br: RegistrationBureau,
    cvk: SplitCVK,
    voters: Dict[str, SplitVoter],
    scenario_id: str,
    selected_voter_id: str,
    selected_candidate: str,
    lang: str,
    candidates: List[str],
) -> List[str]:
    logs = []
    unregistered_str = t(T.UNREGISTERED_USER, lang)

    if selected_voter_id == unregistered_str:
        active_voter = SplitVoter(unregistered_str, is_registered=False)
    else:
        active_voter = voters.get(selected_voter_id)

    if not active_voter:
        return [t(T.ERR_UNREGISTERED, lang, voter=selected_voter_id)]

    cvk_pub_pem = cvk.get_public_key()

    def get_rn_step():
        if active_voter.rn:
            # Voter already got RN in a previous step/scenario, no need to re-request
            return active_voter.rn

        logs.append(t(T.SPLIT_VOTER_REQUESTS_RN, lang, voter=active_voter.voter_id))
        rn = br.register_voter(active_voter.voter_id, lang)
        if not rn:
            logs.append(t(T.SPLIT_ERR_DOUBLE_RN, lang, voter=active_voter.voter_id))
        else:
            logs.append(t(T.SPLIT_BR_ISSUED_RN, lang, voter=active_voter.voter_id))
            active_voter.set_rn(rn)
            cvk.load_rns_from_br(br.get_valid_rns())
        return rn

    def vote_step(cand):
        logs.append(t(T.SPLIT_VOTER_VOTING, lang, voter=active_voter.voter_id))
        try:
            payload = active_voter.vote(cand, cvk_pub_pem)
            logs.append(t(T.SENDING_PAYLOAD, lang))
            cvk.process_vote(payload, lang)
            logs.extend(cvk.get_logs())
            return True
        except ValueError as e:
            logs.append(f"Помилка: {str(e)}")
            return False

    if scenario_id == "scenario_double_rn_split":
        logs.append(t(T.ATTEMPT_1, lang))
        get_rn_step()
        logs.append(t(T.ATTEMPT_2, lang))
        get_rn_step()
        return logs

    elif scenario_id == "scenario_invalid_rn_split":
        # Force an invalid RN
        fake_rn = str(uuid.uuid4())
        logs.append(t(T.SPLIT_VOTER_FAKE_RN, lang, voter=active_voter.voter_id))
        active_voter.set_rn(fake_rn)
        # Assuming they obtained fake_rn without BR knowing
        vote_step(selected_candidate)
        return logs

    elif scenario_id == "scenario_double_vote_split":
        rn = get_rn_step()
        if rn:
            logs.append(t(T.ATTEMPT_1, lang))
            vote_step(selected_candidate)
            logs.append(t(T.ATTEMPT_2, lang))
            # Same voter tries to vote again with same RN
            vote_step(selected_candidate)
        return logs

    elif scenario_id == "scenario_verify_split":
        # First ensure they have an RN and vote if they haven't already
        rn = get_rn_step()

        # If the voter already voted in this session, we shouldn't vote a second time,
        # but for simulation purposes, we assume scenario_verify_split means "Vote AND Verify"
        # Since CVK blocks same RN voting twice, if the RN is already spent, vote_step will fail.
        # So we only vote if the RN is NOT in CVK's used_rns

        has_voted = rn in cvk.used_rns
        if not has_voted:
            if rn:
                vote_step(selected_candidate)
                logs.append(t(T.SPLIT_VOTER_VERIFICATION, lang))
        else:
            logs.append(t(T.SPLIT_VOTER_VERIFICATION, lang))

        # Voter looks up their vote in the CVK's published ballots
        anon_id = active_voter.anonymous_id
        if anon_id in cvk.published_ballots:
            published_cand = cvk.published_ballots[anon_id]["candidate"]
            if published_cand == selected_candidate:
                logs.append(t(T.SPLIT_VERIFY_SUCCESS, lang, cand=published_cand))
            else:
                logs.append(t(T.SPLIT_VERIFY_FAIL_MISMATCH, lang))
        else:
            logs.append(t(T.SPLIT_VERIFY_FAIL_NOT_FOUND, lang))
        return logs

    else:
        # Default normal
        rn = get_rn_step()
        if rn:
            vote_step(selected_candidate)
        return logs
