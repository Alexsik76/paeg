import json
import uuid
import random
from base64 import b64encode, b64decode
from typing import Dict, Any, List, Tuple

from labs.base import BaseCVK, BaseVoter
from core.crypto import RSACryptoSystem
from core.i18n import t, T


class VotingCommission:
    """
    Voting Commission (VC).
    Verifies voter signature and stores partial ballots.
    VC-1 and VC-2 are independent.
    """

    def __init__(self, commission_id: int):
        self.commission_id = commission_id
        # Stores {anonymous_id: encrypted_factor}
        self.partial_ballots: Dict[str, int] = {}

    def process_partial_ballot(self, payload: Dict[str, Any], lang: str) -> bool:
        """
        Verifies signature and stores the factor.
        """
        try:
            message_bytes = b64decode(payload["message"])
            signature_bytes = b64decode(payload["signature"])
            voter_pub_key_bytes = b64decode(payload["public_key"])

            voter_pub_key = RSACryptoSystem.load_public_key(voter_pub_key_bytes)

            # Verify signature
            if not RSACryptoSystem.verify(
                voter_pub_key, message_bytes, signature_bytes
            ):
                return False

            # Extract data
            ballot_data = json.loads(message_bytes.decode("utf-8"))
            anon_id = ballot_data["id"]
            encrypted_factor = ballot_data["encrypted_factor"]

            self.partial_ballots[anon_id] = encrypted_factor
            return True
        except Exception:
            return False

    def get_partial_ballots(self) -> Dict[str, int]:
        return self.partial_ballots.copy()


class SplitFactorVoter(BaseVoter):
    """
    Voter for Lab 4.
    Splits Candidate ID into two factors and sends them to different VCs.
    """

    def __init__(self, voter_id: str, is_registered: bool = True):
        super().__init__(voter_id, is_registered)
        self.crypto_system = RSACryptoSystem()
        self.anonymous_id = str(uuid.uuid4())

    def split_id(self, candidate_id_val: int) -> Tuple[int, int]:
        """
        Finds all divisor pairs and picks one randomly.
        """
        factors = []
        for i in range(1, int(candidate_id_val**0.5) + 1):
            if candidate_id_val % i == 0:
                factors.append((i, candidate_id_val // i))

        # Add reverse pairs as well (e.g., if (2, 6) is there, add (6, 2))
        all_pairs = []
        for f1, f2 in factors:
            all_pairs.append((f1, f2))
            if f1 != f2:
                all_pairs.append((f2, f1))

        return random.choice(all_pairs)

    def vote(
        self,
        candidate_val: int,
        cvk_key_params: Dict[str, int],
    ) -> Tuple[Dict[str, Any], Dict[str, Any], int, int]:
        """
        Splits ID, encrypts factors raw, signs them, and prepares 2 payloads.
        """
        f1, f2 = self.split_id(candidate_val)
        n, e = cvk_key_params["n"], cvk_key_params["e"]

        # Homomorphic Encryption (Textbook RSA)
        ef1 = RSACryptoSystem.raw_encrypt(n, e, f1)
        ef2 = RSACryptoSystem.raw_encrypt(n, e, f2)

        payloads = []
        for factor_val in [ef1, ef2]:
            ballot_data = {
                "id": self.anonymous_id,
                "encrypted_factor": factor_val,
            }
            message = json.dumps(ballot_data, sort_keys=True).encode("utf-8")
            signature = self.crypto_system.sign(message)

            payload = {
                "message": b64encode(message).decode("utf-8"),
                "signature": b64encode(signature).decode("utf-8"),
                "public_key": b64encode(self.crypto_system.get_public_bytes()).decode(
                    "utf-8"
                ),
            }
            payloads.append(payload)

        return payloads[0], payloads[1], f1, f2


class SplitFactorCVK(BaseCVK):
    """
    CVK for Lab 4.
    Collects partial ballots from VCs, performs homomorphic multiplication,
    then decrypts to find the Candidate ID.
    """

    def __init__(self, candidates: List[str], candidate_id_map: Dict[str, int]):
        super().__init__()
        self.crypto_system = RSACryptoSystem()
        self.tallies = {candidate: 0 for candidate in candidates}
        self.id_to_candidate = {v: k for k, v in candidate_id_map.items()}
        self.key_params = self.crypto_system.get_key_parameters()

    def get_key_params(self) -> Dict[str, int]:
        return self.key_params

    def set_language(self, lang: str):
        self.lang = lang

    def process_and_tally(
        self, vc1_ballots: Dict[str, int], vc2_ballots: Dict[str, int], lang: str
    ):
        """
        Joins factors for each unique anonymous ID.
        """
        self.log_action(t(T.FACTOR_CVK_JOINING, lang))

        # Combine by ID
        common_ids = set(vc1_ballots.keys()) & set(vc2_ballots.keys())
        n = self.key_params["n"]

        for anon_id in common_ids:
            c1 = vc1_ballots[anon_id]
            c2 = vc2_ballots[anon_id]

            # Homomorphic joining (multiplication modulo n)
            joint_ciphertext = (c1 * c2) % n

            # Decrypt
            decrypted_id = self.crypto_system.raw_decrypt(joint_ciphertext)

            self.log_action(t(T.FACTOR_CVK_DECRYPTED, lang, val=decrypted_id))

            if decrypted_id in self.id_to_candidate:
                cand = self.id_to_candidate[decrypted_id]
                self.tallies[cand] += 1
                self.log_action(t(T.VOTE_TALLIED, lang, voter=f"ID:{anon_id[:8]}..."))
            else:
                self.log_action(t(T.FACTOR_ERR_TAMPERED, lang, val=decrypted_id))

    def process_vote(self, payload: Any) -> bool:
        """
        Implementation of abstract method from BaseCVK.
        In the split-factor protocol, voting is handled via split commissions
        and finalized in process_and_tally.
        """
        return False
