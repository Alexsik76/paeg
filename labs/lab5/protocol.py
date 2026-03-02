import json
import random
import uuid
from base64 import b64encode, b64decode
from typing import List, Any, Optional

from core.crypto import RSACryptoSystem
from labs.base import BaseVoter


class DecentralizedVoter(BaseVoter):
    """
    Voter for Lab 5.
    Implements a decentralized protocol without a central commission.
    """

    def __init__(self, voter_id: str, is_registered: bool = True):
        super().__init__(voter_id, is_registered)
        self.crypto_system = RSACryptoSystem()
        self.rp = str(uuid.uuid4())[:8]  # Random string (RP)
        self.voted = False
        self.ballots: List[str] = []

    def prepare_ballot(
        self, candidate_id: str, all_voters: List["DecentralizedVoter"]
    ) -> str:
        """
        Phase 1 & 2: Multi-layered encryption.
        Layers for Voter X: A( B( ... X( RP + ... (E( EVP )) ... ) ) )
        Repeated for two rounds.
        """
        # Inner content is the candidate ID (EVP)
        encrypted_data = candidate_id.encode("utf-8")

        # Get all public keys in order (E, D, C, B, A) as per task encryption sequence
        voters_sequence = all_voters[::-1]

        # Two rounds of encryption
        for round_num in range(2):
            for v in voters_sequence:
                if v.voter_id == self.voter_id:
                    # Add RP when encrypting with own key
                    payload = f"{self.rp}|".encode("utf-8") + encrypted_data
                else:
                    payload = encrypted_data

                # Use hybrid encryption from RSACryptoSystem
                encrypted_data = RSACryptoSystem.encrypt(
                    v.crypto_system.public_key, payload
                )

        return b64encode(encrypted_data).decode("utf-8")

    def process_round(
        self,
        encrypted_ballots: List[str],
        prev_signature: Optional[str] = None,
        prev_voter_pub_key: Optional[bytes] = None,
    ) -> List[str]:
        """
        Phase 3 & 4: Decryption round.
        """
        # 1. Verify previous voter's signature
        if prev_signature and prev_voter_pub_key:
            message = "".join(encrypted_ballots).encode("utf-8")
            pub_key = RSACryptoSystem.load_public_key(prev_voter_pub_key)
            if not RSACryptoSystem.verify(pub_key, message, b64decode(prev_signature)):
                raise ValueError("SIGNATURE_MISMATCH")

        decrypted_ballots = []
        rp_found = False

        # 2. Decrypt one layer
        for b64_ballot in encrypted_ballots:
            try:
                decrypted = self.crypto_system.decrypt(b64decode(b64_ballot))

                # Check for RP
                prefix = f"{self.rp}|".encode("utf-8")
                if decrypted.startswith(prefix):
                    rp_found = True
                    remainder = decrypted[len(prefix) :]
                else:
                    remainder = decrypted

                # Identify if remainder is a layer or plaintext
                try:
                    data_str = remainder.decode("utf-8")
                    try:
                        parsed = json.loads(data_str)
                        if (
                            isinstance(parsed, dict)
                            and "key" in parsed
                            and "data" in parsed
                        ):
                            # It's another encrypted layer (hybrid payload)
                            decrypted_ballots.append(
                                b64encode(remainder).decode("utf-8")
                            )
                        else:
                            # It's final candidate ID or other non-layer data
                            decrypted_ballots.append(data_str)
                    except (json.JSONDecodeError, TypeError):
                        # Not JSON, treat as plaintext
                        decrypted_ballots.append(data_str)
                except UnicodeDecodeError:
                    # Binary data, must be an encrypted layer
                    decrypted_ballots.append(b64encode(remainder).decode("utf-8"))

            except Exception:
                raise ValueError("DECRYPTION_FAILED")

        # 3. Verify RP presence for self if the voter cast a ballot
        if self.voted and not rp_found:
            raise ValueError("RP_NOT_FOUND")

        # 4. Shuffle
        random.shuffle(decrypted_ballots)

        return decrypted_ballots

    def sign_ballots(self, ballots: List[str]) -> bytes:
        message = "".join(ballots).encode("utf-8")
        return self.crypto_system.sign(message)

    def vote(self, candidate_id: str, _: Any) -> Any:
        # BaseVoter requirement, but Lab 5 uses a different flow.
        return None
