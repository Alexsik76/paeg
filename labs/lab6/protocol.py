import random
import uuid
from typing import Dict, Any, List, Tuple, Set

from labs.base import BaseCVK, BaseVoter
from core.crypto import RSACryptoSystem
from core.i18n import t, T


def bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, "big")


class RegistrationBureau:
    """
    Registration Bureau (RB).
    Registers voters and provides them with authorization to vote.
    In this protocol, it might also act as a proxy for the CEC's blind signature.
    """

    def __init__(self):
        self.registered_voters: Set[str] = set()

    def register(self, voter_id: str) -> bool:
        self.registered_voters.add(voter_id)
        return True

    def is_registered(self, voter_id: str) -> bool:
        return voter_id in self.registered_voters


class LowLevelCommission:
    """
    Low-Level Commission (LC).
    Collects ballot particles, verifies digital signatures,
    and transfers data to the middle-level election commission.
    """

    def __init__(self, commission_id: int):
        self.commission_id = commission_id
        # Stores {anonymous_id: (partial_ballot, signature)}
        self.partial_ballots: Dict[str, Tuple[int, int]] = {}

    def process_partial(
        self,
        anon_id: str,
        m_prime_prime: int,
        signature: int,
        pub_key_params: Dict[str, int],
    ) -> bool:
        """
        Verifies blind signature and stores the particle.
        """
        n, e = pub_key_params["n"], pub_key_params["e"]
        # Blind signature verification: m == s^e mod n
        if m_prime_prime == pow(signature, e, n):
            self.partial_ballots[anon_id] = (m_prime_prime, signature)
            return True
        return False


class MiddleLevelCommission:
    """
    Middle-Level Commission (MC).
    Collects data from its LCs, joins ballots, decrypts them,
    counts votes, and transfers data to CEC.
    Each MC handles 2 LCs.
    """

    def __init__(
        self,
        commission_id: int,
        crypto_system: RSACryptoSystem,
        candidates: List[str],
        id_to_candidate: Dict[int, str],
    ):
        self.commission_id = commission_id
        self.crypto_system = crypto_system
        self.candidates = candidates
        self.id_to_candidate = id_to_candidate
        self.tallies: Dict[str, int] = {cand: 0 for cand in candidates}
        self.voted_anon_ids: Set[str] = set()

    def aggregate_and_count(
        self, lc1: LowLevelCommission, lc2: LowLevelCommission, n: int, lang: str
    ) -> List[str]:
        """
        Joins particles from two LCs and decrypts the ballot.
        """
        logs = []
        common_ids = set(lc1.partial_ballots.keys()) & set(lc2.partial_ballots.keys())

        for anon_id in common_ids:
            if anon_id in self.voted_anon_ids:
                continue

            m1, s1 = lc1.partial_ballots[anon_id]
            m2, s2 = lc2.partial_ballots[anon_id]

            # Reconstruct joint ciphertext: C = C1 * C2 mod n
            joint_ciphertext = (m1 * m2) % n

            # Decrypt joint ciphertext
            try:
                decrypted_id = self.crypto_system.raw_decrypt(joint_ciphertext)
                if decrypted_id in self.id_to_candidate:
                    candidate = self.id_to_candidate[decrypted_id]
                    self.tallies[candidate] += 1
                    self.voted_anon_ids.add(anon_id)
                    logs.append(
                        t(
                            T.LAB6_MC_DECRYPTED,
                            lang,
                            id=self.commission_id,
                            anon_id=anon_id[:8],
                            candidate=candidate,
                            cand_id=decrypted_id,
                        )
                    )
                else:
                    logs.append(
                        f"MC-{self.commission_id}: ERROR: Decrypted ID {decrypted_id} not in candidates list."
                    )
            except Exception as e:
                logs.append(
                    f"MC-{self.commission_id}: ERROR decrypting ballot for ID {anon_id[:8]}: {str(e)}"
                )

        return logs


class BlindSplitCVK(BaseCVK):
    """
    Central Election Commission (CEC).
    Implementation of blind signatures, collection of data from MCs,
    general counting, and publication.
    """

    def __init__(self, candidates: List[str], candidate_id_map: Dict[str, int]):
        super().__init__()
        self.crypto_system = RSACryptoSystem()
        self.candidates = candidates
        self.id_to_candidate = {v: k for k, v in candidate_id_map.items()}
        self.tallies = {cand: 0 for cand in candidates}
        self.voters_signed: Set[str] = set()

        # Key parameters for blinding
        params = self.crypto_system.get_key_parameters()
        self.n = params["n"]
        self.e = params["e"]
        priv_numbers = self.crypto_system.private_key.private_numbers()
        self.d = priv_numbers.d

    def get_public_params(self) -> Dict[str, int]:
        return {"n": self.n, "e": self.e}

    def set_language(self, lang: str):
        self.lang = lang

    def sign_blind_parts(
        self, voter_id: str, blinded_parts: Tuple[int, int]
    ) -> Tuple[int, int]:
        """
        Signs two blinded particles if the voter is registered and hasn't signed before.
        """
        if voter_id not in self.registered_voters:
            return None
        if voter_id in self.voters_signed:
            return None

        # s' = m'^d mod n
        s1_prime = pow(blinded_parts[0], self.d, self.n)
        s2_prime = pow(blinded_parts[1], self.d, self.n)

        self.voters_signed.add(voter_id)
        return s1_prime, s2_prime

    def aggregate_mc_results(self, mcs: List[MiddleLevelCommission]):
        """
        Sums up tallies from all Middle-Level Commissions.
        """
        for cand in self.candidates:
            self.tallies[cand] = sum(mc.tallies[cand] for mc in mcs)

    def process_vote(self, payload: Any) -> bool:
        # Final aggregation is done via aggregate_mc_results
        return True


class BlindSplitVoter(BaseVoter):
    """
    Voter for Lab 6.
    Splits encrypted ballot, blinds parts, gets signatures, unblinds,
    and sends parts to LCs.
    """

    def __init__(self, voter_id: str, is_registered: bool = True):
        super().__init__(voter_id, is_registered)
        self.crypto_system = RSACryptoSystem()
        self.anonymous_id = str(uuid.uuid4())
        self.blinding_factors: List[int] = []

    def prepare_vote(self, candidate_val: int, n: int, e: int) -> Tuple[int, int]:
        """
        1. Encrypt candidate_val: C = m^e mod n
        2. Split C into C1, C2: C = C1 * C2 mod n
        3. Blind C1, C2: C_prime = C * r^e mod n
        """
        # Encrypt the candidate value (textbook RSA for homomorphic split)
        c = pow(candidate_val, e, n)

        # Split C into C1, C2
        while True:
            c1 = random.randint(2, n - 1)
            try:
                c1_inv = pow(c1, -1, n)
                c2 = (c * c1_inv) % n
                break
            except ValueError:
                continue

        self.parts = (c1, c2)

        # Blind both parts
        blinded_parts = []
        self.blinding_factors = []
        for part in self.parts:
            r = random.randint(2, n - 1)
            # Actually should be coprime to n, but for RSA it's 99.9%
            self.blinding_factors.append(r)
            blinded_part = (part * pow(r, e, n)) % n
            blinded_parts.append(blinded_part)

        return tuple(blinded_parts)

    def unblind_signatures(
        self, signed_blinded_parts: Tuple[int, int], n: int
    ) -> Tuple[int, int]:
        """
        Unblinds the signatures: s = s_prime * r^-1 mod n
        """
        unblinded_sigs = []
        for i in range(2):
            s_prime = signed_blinded_parts[i]
            r = self.blinding_factors[i]
            r_inv = pow(r, -1, n)
            s = (s_prime * r_inv) % n
            unblinded_sigs.append(s)

        self.signatures = tuple(unblinded_sigs)
        return self.signatures

    def vote(self, candidate_id: str, cvk_public_key: bytes) -> Any:
        # This method is required by BaseVoter, but Lab 6 uses a multi-step process.
        # It will be orchestrated in the scenario.
        pass
