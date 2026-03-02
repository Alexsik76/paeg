import json
import uuid
from base64 import b64encode, b64decode
from typing import Dict, Any, List, Optional

from labs.base import BaseCVK, BaseVoter
from core.crypto import RSACryptoSystem
from core.i18n import t, T


class RegistrationBureau:
    """
    Bureau of Registration (BR).
    Responsible for identifying voters and issuing Registration Numbers (RNs).
    BR knows WHO is voting but does not see what they vote for.
    """

    def __init__(self):
        # Maps voter_id -> Registration Number (RN)
        self.issued_rns: Dict[str, str] = {}
        # List of all valid RNs to send to CVK
        self.valid_rns: List[str] = []

    def register_voter(self, voter_id: str, lang: str) -> Optional[str]:
        """
        Issues an RN to a voter.
        Returns the RN if successful, or None if the voter already received one.
        """
        if voter_id in self.issued_rns:
            return None  # Voter already received an RN, prevent double RN

        # Generate a secure random Registration Number
        rn = str(uuid.uuid4())
        self.issued_rns[voter_id] = rn
        self.valid_rns.append(rn)
        return rn

    def get_valid_rns(self) -> List[str]:
        """
        Returns the list of all valid RNs to the CVK.
        Crucially, this list does NOT contain voter IDs, preserving anonymity.
        """
        return self.valid_rns.copy()


class SplitVoter(BaseVoter):
    """
    Voter in the Split Protocol (Lab 3).
    Gets an RN from BR, generates an anonymous ID, and sends ballot to CVK.
    """

    def __init__(self, voter_id: str, is_registered: bool = True):
        super().__init__(voter_id, is_registered)
        self.crypto_system = RSACryptoSystem()
        self.rn: Optional[str] = None
        self.anonymous_id: str = str(uuid.uuid4())

    def set_rn(self, rn: str):
        self.rn = rn

    def vote(
        self,
        candidate_id: str,
        cvk_public_key_pem: bytes,
    ) -> Dict[str, Any]:
        """
        Prepares the ballot: {id, rn, candidate}
        Signs the ballot with Voter's private key.
        Encrypts the payload with CVK's public key.
        """
        if not self.rn:
            raise ValueError("Voter does not have an RN from the Registration Bureau.")

        ballot_data = {
            "id": self.anonymous_id,
            "rn": self.rn,
            "candidate": candidate_id,
        }

        message = json.dumps(ballot_data, sort_keys=True).encode("utf-8")

        # 1. Sign
        signature = self.crypto_system.sign(message)

        # 2. Encrypt
        cvk_pub_key = RSACryptoSystem.load_public_key(cvk_public_key_pem)

        # Send public key PEM inside the payload so CVK can verify the signature
        # without knowing the voter_id.
        payload_data = {
            "message": b64encode(message).decode("utf-8"),
            "signature": b64encode(signature).decode("utf-8"),
            "public_key": b64encode(self.crypto_system.get_public_bytes()).decode(
                "utf-8"
            ),
        }

        payload_json = json.dumps(payload_data).encode("utf-8")
        encrypted_payload = RSACryptoSystem.encrypt(cvk_pub_key, payload_json)

        return {"encrypted_data": b64encode(encrypted_payload).decode("utf-8")}


class SplitCVK(BaseCVK):
    """
    Central Election Commission for Split Protocol (Lab 3).
    Receives valid RNs from BR. Validates incoming votes against RNs.
    Does not know voter identities, tallies anonymous IDs.
    """

    def __init__(self, candidates: List[str]):
        super().__init__()
        self.crypto_system = RSACryptoSystem()
        self.tallies = {candidate: 0 for candidate in candidates}
        self.valid_rns: List[str] = []
        self.used_rns = set()
        # To allow voters to verify their vote: stores {id: signed_ballot_data}
        self.published_ballots: Dict[str, Dict[str, Any]] = {}

    def get_public_key(self) -> bytes:
        return self.crypto_system.get_public_bytes()

    def set_language(self, lang: str):
        self.lang = lang

    def load_rns_from_br(self, rns: List[str]):
        """
        Loads the valid Registration Numbers provided by the Registration Bureau.
        """
        self.valid_rns = rns

    def process_vote(self, payload: Dict[str, Any], lang: str) -> bool:
        """
        CVK decrypts the payload, checks the signature, and verifies the RN.
        """
        try:
            self.log_action(t(T.RECEIVED_PAYLOAD, lang))
            encrypted_data = b64decode(payload.get("encrypted_data", ""))

            # Decrypt
            decrypted_json = self.crypto_system.decrypt(encrypted_data)
            self.log_action(t(T.DECRYPTED_SUCCESS, lang))

            payload_data = json.loads(decrypted_json.decode("utf-8"))

            message_bytes = b64decode(payload_data["message"])
            signature_bytes = b64decode(payload_data["signature"])
            voter_pub_key_bytes = b64decode(payload_data["public_key"])

            voter_pub_key = RSACryptoSystem.load_public_key(voter_pub_key_bytes)

            # Verify signature
            if not RSACryptoSystem.verify(
                voter_pub_key, message_bytes, signature_bytes
            ):
                self.log_action(t(T.ERR_SIGNATURE, lang))
                return False

            self.log_action(t(T.SIG_VERIFIED, lang))

            # Extract ballot
            ballot = json.loads(message_bytes.decode("utf-8"))
            candidate = ballot.get("candidate")
            rn = ballot.get("rn")
            anonymous_id = ballot.get("id")

            # Verify RN is valid
            if rn not in self.valid_rns:
                self.log_action(t(T.ERR_INVALID_RN, lang))
                return False

            # Verify RN is not already used
            if rn in self.used_rns:
                self.log_action(t(T.ERR_RN_ALREADY_USED, lang))
                return False

            # Tally vote
            if candidate not in self.tallies:
                self.log_action(t(T.WARN_UNKNOWN_CAND, lang, candidate=candidate))
                return False

            self.used_rns.add(rn)
            self.tallies[candidate] += 1

            # Store in published ballots for verification
            self.published_ballots[anonymous_id] = {
                "candidate": candidate,
                "message": payload_data["message"],
                "signature": payload_data["signature"],
            }

            self.log_action(t(T.VOTE_TALLIED, lang, voter=f"ID:{anonymous_id[:8]}..."))
            return True

        except Exception as e:
            self.log_action(t(T.ERR_PROCESS_VOTE, lang, error=str(e)))
            return False
