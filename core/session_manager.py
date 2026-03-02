import streamlit as st
from typing import Dict, Any

from core.i18n import t, T
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


def reset_lab_state(lab_config: Dict[str, Any], selected_lab_id: str, lang: str) -> None:
    """
    Resets the CVK and voter states for the selected lab.
    Acts as a Factory for protocol objects.
    """
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
    init_msg = ""

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
            MiddleLevelCommission(1, st.session_state.cvk.crypto_system, candidates, st.session_state.cvk.id_to_candidate),
            MiddleLevelCommission(2, st.session_state.cvk.crypto_system, candidates, st.session_state.cvk.id_to_candidate),
        ]
        st.session_state.lcs = [
            LowLevelCommission(1), LowLevelCommission(2),
            LowLevelCommission(3), LowLevelCommission(4),
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