import json
import random
import uuid
from base64 import b64encode, b64decode
from typing import Dict, Any, List, Tuple

from labs.base import BaseCVK, BaseVoter
from core.crypto import RSACryptoSystem
from core.i18n import t, T


def bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, "big")


def int_to_bytes(i: int) -> bytes:
    return i.to_bytes((i.bit_length() + 7) // 8, "big")


class BlindVoter(BaseVoter):
    def __init__(self, voter_id: str, is_registered: bool = True):
        super().__init__(voter_id, is_registered)
        # We don't necessarily need a full RSACryptoSystem for the voter in Lab 2
        # because the signature comes from CVK and encryption can be done with CVK's pub key,
        # but let's keep it if needed.
        self.crypto_system = RSACryptoSystem()
        self.rnd_id = str(uuid.uuid4())

        # State for the blinding process
        self.ballots: List[Dict[str, Dict[str, Any]]] = []
        self.multipliers: List[Dict[str, int]] = []
        self.blinded_sets: List[Dict[str, int]] = []
        self.chosen_unblinded_set: Dict[str, int] = {}
        self.chosen_ballots_set: Dict[str, Any] = {}

    def prepare_blinded_sets(
        self, e: int, n: int, candidates: List[str]
    ) -> List[Dict[str, int]]:
        """
        Generates 10 sets of ballots. Each set contains 1 ballot per candidate.
        Blinds them with random multipliers.
        Returns the 10 blinded sets.
        """
        self.ballots = []
        self.multipliers = []
        self.blinded_sets = []

        # We will generate a new rnd_id per session to allow the voter to attempt again if rejected?
        # A single vote session uses one rnd_id.
        self_rnd_id = self.rnd_id

        for _ in range(10):
            ballot_set = {}
            mult_set = {}
            blinded_set = {}
            for cand in candidates:
                ballot = {"id": self_rnd_id, "candidate": cand}
                ballot_bytes = json.dumps(ballot, sort_keys=True).encode("utf-8")
                m = bytes_to_int(ballot_bytes)

                # Random multiplier coprime to n
                while True:
                    r = random.randrange(2, n - 1)
                    # For RSA moduli, a random number is almost certainly coprime to n,
                    # but technically we could check math.gcd(r, n) == 1
                    break

                # m' = m * r^e mod n
                m_prime = (m * pow(r, e, n)) % n

                ballot_set[cand] = ballot
                mult_set[cand] = r
                blinded_set[cand] = m_prime

            self.ballots.append(ballot_set)
            self.multipliers.append(mult_set)
            self.blinded_sets.append(blinded_set)

        return self.blinded_sets

    def provide_multipliers(self, indices: List[int]) -> List[Dict[str, int]]:
        """
        Returns the multipliers for the requested indices so CVK can verify them.
        """
        return [self.multipliers[i] for i in indices]

    def process_signed_set(
        self, signed_set: Dict[str, int], chosen_index: int, n: int
    ) -> None:
        """
        Unblinds the signatures received from CVK.
        s = s_prime * r^-1 mod n
        """
        self.chosen_unblinded_set = {}
        self.chosen_ballots_set = self.ballots[chosen_index]
        mult_set = self.multipliers[chosen_index]

        for cand, s_prime in signed_set.items():
            r = mult_set[cand]
            r_inv = pow(r, -1, n)
            s = (s_prime * r_inv) % n
            self.chosen_unblinded_set[cand] = s

    def vote(self, candidate_id: str, cvk_public_key_pem: bytes) -> Dict[str, Any]:
        """
        Casts the actual vote using the unblinded signature and the original ballot.
        Encrypts the payload with CVK's public key.
        """
        if candidate_id not in self.chosen_unblinded_set:
            raise ValueError(f"Candidate {candidate_id} not in the signed set.")

        ballot = self.chosen_ballots_set[candidate_id]
        signature = self.chosen_unblinded_set[candidate_id]

        payload_data = {"ballot": ballot, "signature": signature}

        payload_json = json.dumps(payload_data).encode("utf-8")

        cvk_pub_key = RSACryptoSystem.load_public_key(cvk_public_key_pem)
        encrypted_payload = RSACryptoSystem.encrypt(cvk_pub_key, payload_json)

        return {"encrypted_data": b64encode(encrypted_payload).decode("utf-8")}


class BlindCVK(BaseCVK):
    def __init__(self, candidates: list):
        super().__init__()
        self.crypto_system = RSACryptoSystem()
        self.candidates = candidates
        self.tallies = {candidate: 0 for candidate in candidates}
        self.voters_received_signature = set()
        self.used_rnd_ids = set()

        priv_numbers = self.crypto_system.private_key.private_numbers()
        pub_numbers = self.crypto_system.public_key.public_numbers()
        self.n = pub_numbers.n
        self.e = pub_numbers.e
        self.d = priv_numbers.d

    def get_public_key(self) -> bytes:
        return self.crypto_system.get_public_bytes()

    def get_public_numbers(self) -> Tuple[int, int]:
        return self.e, self.n

    def set_language(self, lang: str):
        self.lang = lang

    def choose_sets_to_check(self) -> Tuple[int, List[int]]:
        """
        Chooses 1 set to sign, and 9 sets to check.
        Returns (chosen_index, checked_indices)
        """
        indices = list(range(10))
        chosen_index = random.choice(indices)
        checked_indices = [i for i in indices if i != chosen_index]
        return chosen_index, checked_indices

    def verify_and_sign(
        self,
        voter_id: str,
        blinded_sets: List[Dict[str, int]],
        checked_indices: List[int],
        multipliers_list: List[Dict[str, int]],
        chosen_index: int,
        lang: str,
    ) -> Dict[str, int]:
        """
        Verifies the 9 sets using the provided multipliers.
        If valid, signs the 10th set.
        """
        if voter_id not in self.registered_voters:
            self.log_action(t(T.ERR_UNREGISTERED, lang, voter=voter_id))
            return {}

        if voter_id in self.voters_received_signature:
            self.log_action(t(T.BLIND_CVK_ALREADY_SIGNED, lang, voter=voter_id))
            return {}

        # Verify the 9 sets
        expected_id = None
        for i, idx in enumerate(checked_indices):
            blinded_set = blinded_sets[idx]
            mult_set = multipliers_list[i]

            for cand in self.candidates:
                m_prime = blinded_set[cand]
                r = mult_set[cand]

                # m = m_prime * (r^e)^-1 mod n
                r_e = pow(r, self.e, self.n)
                r_e_inv = pow(r_e, -1, self.n)
                m = (m_prime * r_e_inv) % self.n

                try:
                    ballot_bytes = int_to_bytes(m)
                    ballot = json.loads(ballot_bytes.decode("utf-8"))
                    if ballot.get("candidate") != cand:
                        self.log_action(t(T.BLIND_CVK_REJECTED, lang))
                        return {}
                    if expected_id is None:
                        expected_id = ballot.get("id")
                    elif expected_id != ballot.get("id"):
                        self.log_action(t(T.BLIND_CVK_REJECTED, lang))
                        return {}
                except Exception:
                    self.log_action(t(T.BLIND_CVK_REJECTED, lang))
                    return {}

        # All 9 sets valid. Sign the chosen index.
        signed_set = {}
        for cand, m_prime in blinded_sets[chosen_index].items():
            # s' = m'^d mod n
            s_prime = pow(m_prime, self.d, self.n)
            signed_set[cand] = s_prime

        self.voters_received_signature.add(voter_id)
        self.log_action(t(T.BLIND_CVK_SIGNED, lang))
        return signed_set

    def process_vote(self, payload: Dict[str, Any], lang: str) -> bool:
        """
        CVK processes the final encrypted cast vote.
        """
        try:
            self.log_action(t(T.RECEIVED_PAYLOAD, lang))
            encrypted_data = b64decode(payload.get("encrypted_data", ""))

            # Decrypt
            decrypted_json = self.crypto_system.decrypt(encrypted_data)
            self.log_action(t(T.DECRYPTED_SUCCESS, lang))

            payload_data = json.loads(decrypted_json.decode("utf-8"))
            ballot = payload_data["ballot"]
            signature = payload_data["signature"]

            voter_rnd_id = ballot.get("id")
            candidate = ballot.get("candidate")

            # Verify signature: m == s^e mod n
            ballot_bytes = json.dumps(ballot, sort_keys=True).encode("utf-8")
            m = bytes_to_int(ballot_bytes)

            if m != pow(signature, self.e, self.n):
                self.log_action(t(T.BLIND_ERR_TAMPERED, lang))
                return False

            self.log_action(t(T.SIG_VERIFIED, lang))

            # Check double voting via unique rnd_id
            if voter_rnd_id in self.used_rnd_ids:
                self.log_action(t(T.BLIND_ERR_ID_USED, lang, voter_rnd_id=voter_rnd_id))
                return False

            # Tally vote
            if candidate not in self.tallies:
                self.log_action(t(T.WARN_UNKNOWN_CAND, lang, candidate=candidate))
                return False

            self.used_rnd_ids.add(voter_rnd_id)
            self.tallies[candidate] += 1
            # In blind protocol, we don't know the voter's real identity here, so we log rnd_id
            self.log_action(t(T.VOTE_TALLIED, lang, voter=f"ID:{voter_rnd_id[:8]}..."))
            return True

        except Exception as e:
            self.log_action(t(T.ERR_PROCESS_VOTE, lang, error=str(e)))
            return False
