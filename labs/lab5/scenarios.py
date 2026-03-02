import random
from typing import List, Dict
from base64 import b64encode
from labs.base import BaseScenarioRunner
from labs.lab5.protocol import DecentralizedVoter
from core.i18n import t, T


def run_simulate_all_decentralized(
    voters: Dict[str, DecentralizedVoter],
    candidates: List[str],
    candidate_id_map: Dict[str, int],
    lang: str,
    tamper_type: str = None,
    tamper_voter_id: str = None,
    only_voter_id: str = None,
    specific_candidate: str = None,
) -> List[str]:
    logs = [t(T.DECENTRALIZED_INIT, lang)]
    voter_list = list(voters.values())

    # Check if any voter has already voted
    for voter in voter_list:
        if voter.voted:
            # We use the same error key as Lab 1 for consistency
            logs.append(t(T.ERR_DOUBLE_VOTE, lang, voter=voter.voter_id))
            return logs

    # Phase 1 & 2: Encryption
    all_encrypted_ballots = []
    participating_voter_ids = []

    for v_id, voter in voters.items():
        if only_voter_id and v_id != only_voter_id:
            continue

        # Pick candidate
        cand_name = (
            specific_candidate
            if (only_voter_id and specific_candidate)
            else random.choice(candidates)
        )
        cand_val = str(candidate_id_map[cand_name])

        logs.append(t(T.DECENTRALIZED_ROUND_ENC, lang, voter=v_id))
        encrypted = voter.prepare_ballot(cand_val, voter_list)
        all_encrypted_ballots.append(encrypted)

        if tamper_type == "double_vote" and tamper_voter_id == v_id:
            # Voter injects a second ballot
            logs.append(
                f"--- [ЗАГРОЗА]: {v_id} готує другий (дублікатний) бюлетень ---"
            )
            extra_encrypted = voter.prepare_ballot(cand_val, voter_list)
            all_encrypted_ballots.append(extra_encrypted)

        voter.voted = True
        participating_voter_ids.append(v_id)
        logs.append(t(T.DECENTRALIZED_VOTER_READY, lang, voter=v_id))

    def reset_voted(v_list: List[DecentralizedVoter]):
        for v in v_list:
            v.voted = False

    # Phase 3 & 4: Decryption Rounds
    current_ballots = all_encrypted_ballots
    total_expected = len(participating_voter_ids)

    def abort_with_reset(logs_list: List[str]):
        # Reset voted status for THIS run if protocol failed, allowing retry
        reset_voted([voters[vid] for vid in participating_voter_ids])
        return logs_list

    # We do two rounds of decryption.
    for round_num in [1, 2]:
        prev_sig = None
        prev_pub_key = None

        for i, voter in enumerate(voter_list):
            v_id = voter.voter_id
            logs.append(t(T.DECENTRALIZED_ROUND_DEC, lang, round=round_num, voter=v_id))

            # Tampering Scenarios (Mid-round)
            if tamper_voter_id == v_id:
                if tamper_type == "tamper":
                    # Voter A modifies a random ballot
                    idx = random.randint(0, len(current_ballots) - 1)
                    current_ballots[idx] = current_ballots[idx][:-4] + "AAAA"
                    logs.append(f"--- [ЗАГРОЗА]: {v_id} підмінив один із бюлетенів ---")

                elif tamper_type == "count_add":
                    # Voter A adds an extra ballot
                    extra = current_ballots[0]
                    current_ballots.append(extra)
                    logs.append(f"--- [ЗАГРОЗА]: {v_id} додав зайвий бюлетень ---")

                elif tamper_type == "count_remove":
                    # Voter A removes a ballot
                    current_ballots.pop()
                    logs.append(f"--- [ЗАГРОЗА]: {v_id} вилучив один бюлетень ---")

            # Check expected ballot count
            if len(current_ballots) != total_expected:
                logs.append(
                    t(
                        T.DECENTRALIZED_ERR_COUNT,
                        lang,
                        voter=v_id,
                        count=len(current_ballots),
                        expected=total_expected,
                    )
                )
                logs.append(
                    "--- [ПРИМІТКА]: Протокол перервано через порушення цілісності кошика ---"
                )
                return abort_with_reset(logs)

            try:
                current_ballots = voter.process_round(
                    current_ballots, prev_sig, prev_pub_key
                )
                logs.append(t(T.DECENTRALIZED_SHUFFLING, lang, voter=v_id))

                # Sign for next voter
                prev_sig = b64encode(voter.sign_ballots(current_ballots)).decode(
                    "utf-8"
                )
                prev_pub_key = voter.crypto_system.get_public_bytes()

            except ValueError as e:
                if str(e) == "SIGNATURE_MISMATCH" or str(e) == "DECRYPTION_FAILED":
                    logs.append(t(T.DECENTRALIZED_ERR_TAMPERED, lang, voter=v_id))
                elif str(e) == "RP_NOT_FOUND":
                    logs.append(
                        f"❌ Error: Voter {v_id} could NOT find their ballot RP!"
                    )
                else:
                    logs.append(f"❌ Error for {v_id}: {str(e)}")

                logs.append(
                    "--- [ПРИМІТКА]: Це колективний протокол. Один збій робить весь підрахунок неможливим для захисту анонімності. ---"
                )
                return abort_with_reset(logs)

    # Final Phase: Tally
    logs.append(t(T.DECENTRALIZED_FINAL_TALLY, lang))
    id_to_candidate = {str(v): k for k, v in candidate_id_map.items()}

    for item in current_ballots:
        if item in id_to_candidate:
            logs.append(t(T.DECENTRALIZED_VOTE_FOUND, lang, cand=id_to_candidate[item]))
        else:
            logs.append(f"❌ Невідомий або пошкоджений голос: {item}")

    logs.append(t(T.DECENTRALIZED_SUCCESS, lang))
    reset_voted(voter_list)
    return logs


class DecentralizedScenarioRunner(BaseScenarioRunner):
    """
    Scenario runner for Lab 5 (Decentralized Protocol).
    """

    def __init__(
        self,
        voters: Dict[str, DecentralizedVoter],
        candidates: List[str],
        candidate_id_map: Dict[str, int],
        lang: str,
    ):
        super().__init__(voters, candidates, lang)
        self.candidate_id_map = candidate_id_map

    def run(
        self, scenario_id: str, selected_voter_id: str, selected_candidate: str
    ) -> List[str]:
        if scenario_id == "scenario_simulate_all_decentralized":
            return run_simulate_all_decentralized(
                self.voters, self.candidates, self.candidate_id_map, self.lang
            )
        else:
            return run_single_voter_scenario_decentralized(
                self.voters,
                scenario_id,
                self.candidates,
                self.candidate_id_map,
                self.lang,
                selected_voter_id,
                selected_candidate,
            )


def run_single_voter_scenario_decentralized(
    voters: Dict[str, DecentralizedVoter],
    scenario_id: str,
    candidates: List[str],
    candidate_id_map: Dict[str, int],
    lang: str,
    selected_voter_id: str = None,
    selected_candidate: str = None,
) -> List[str]:

    if scenario_id == "scenario_normal_decentralized":
        # Simulate normal voting (1 voter)
        return run_simulate_all_decentralized(
            voters,
            candidates,
            candidate_id_map,
            lang,
            only_voter_id=selected_voter_id,
            specific_candidate=selected_candidate,
        )

    elif scenario_id == "scenario_double_vote_decentralized":
        # Simulate a voter attempting to inject two ballots
        return run_simulate_all_decentralized(
            voters,
            candidates,
            candidate_id_map,
            lang,
            tamper_type="double_vote",
            tamper_voter_id="voter_1",
            only_voter_id=selected_voter_id,
            specific_candidate=selected_candidate,
        )

    elif scenario_id == "scenario_tamper_decentralized":
        return run_simulate_all_decentralized(
            voters,
            candidates,
            candidate_id_map,
            lang,
            tamper_type="tamper",
            tamper_voter_id="voter_1",
        )

    elif scenario_id == "scenario_count_decentralized":
        return run_simulate_all_decentralized(
            voters,
            candidates,
            candidate_id_map,
            lang,
            tamper_type="count_add",
            tamper_voter_id="voter_1",
        )

    return ["Invalid scenario"]
