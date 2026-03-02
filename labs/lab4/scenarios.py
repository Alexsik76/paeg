import json
import random
from typing import Dict, List, Any, Optional

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

        logs.append(t(T.FACTOR_SEND_V2, lang))
        v2_ok = vc2.process_partial_ballot(p2, lang)
        if v2_ok:
            logs.append(t(T.FACTOR_VC_VERIFIED, lang))

    # 3. CVK joins and tallies
    cvk.process_and_tally(vc1.get_partial_ballots(), vc2.get_partial_ballots(), lang)
    logs.extend(cvk.get_logs())

    # Calculate success based on CVK tallies
    total_tallied = sum(cvk.tallies.values())
    if total_tallied == total_count:
        logs.append(t(T.SIMULATION_OK, lang, count=total_count))
    else:
        logs.append(
            t(
                T.SIMULATION_ERRORS,
                lang,
                success_count=total_tallied,
                total_count=total_count,
            )
        )

    return logs


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
        # We need to re-encrypt a different factor for it to be "validly" tampered or just random junk
        # Text says: "Оскільки перед підрахунком голосів всі ВК публікують частинки..."
        # Let's say VC-1 changes f1 value.

        # Extract original factor
        orig_msg = json.loads(active_voter.b64decode(p1["message"]).decode("utf-8"))
        orig_val = orig_msg["encrypted_factor"]

        # Tampered val (random multiplier)
        tampered_val = (orig_val * 7) % key_params["n"]

        # Inject it into a fake payload for VC-1 (mimicking internal VC tampering)
        # Note: VC-1 doesn't verify its own internal metadata, it just publishes it later.
        # But here we simulate it by modifying what's stored in VC-1.

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
        vc1.process_partial_ballot(p1, lang)
        logs.append(t(T.FACTOR_VC_VERIFIED, lang))

    # VC-2 always receives its factor
    logs.append(t(T.FACTOR_SEND_V2, lang))
    vc2.process_partial_ballot(p2, lang)
    logs.append(t(T.FACTOR_VC_VERIFIED, lang))

    # 3. CVK joins and tallies
    cvk.process_and_tally(vc1.get_partial_ballots(), vc2.get_partial_ballots(), lang)
    logs.extend(cvk.get_logs())

    return logs


# Add b64decode/encode wrappers to Voter for tampering logic if needed,
# but easier to just use base64 import.
import base64


def b64_d(s):
    return base64.b64decode(s)
