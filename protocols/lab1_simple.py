"""
Implementation of Lab 1: Simple Protocol.
"""

import json
from base64 import b64encode, b64decode
from typing import Dict, Any, Optional

from protocols.base import BaseVoter, BaseCVK
from core.crypto import RSACryptoSystem


class SimpleVoter(BaseVoter):
    def __init__(self, voter_id: str, is_registered: bool = True):
        super().__init__(voter_id, is_registered)
        # Initialize RSA keys for the voter
        self.crypto_system = RSACryptoSystem()

    def vote(
        self,
        candidate_id: str,
        cvk_public_key_pem: bytes,
        simulate_tampering: bool = False,
    ) -> Dict[str, Any]:
        """
        1. Voter signs the ballot (candidate ID) with their private key.
        2. Voter encrypts the signed ballot with CVK's public key.
        """
        # Create ballot payload
        ballot_data = {"voter_id": self.voter_id, "candidate": candidate_id}

        message = json.dumps(ballot_data).encode("utf-8")

        # 1. Sign
        signature = self.crypto_system.sign(message)

        if simulate_tampering:
            # Tamper the message after signing
            ballot_data["candidate"] = "Hacker"
            message = json.dumps(ballot_data).encode("utf-8")

        # 2. Encrypt
        cvk_pub_key = RSACryptoSystem.load_public_key(cvk_public_key_pem)

        # We need to send both message and signature encrypted
        payload_data = {
            "message": b64encode(message).decode("utf-8"),
            "signature": b64encode(signature).decode("utf-8"),
            "voter_public_key": b64encode(self.crypto_system.get_public_bytes()).decode(
                "utf-8"
            ),
        }

        payload_json = json.dumps(payload_data).encode("utf-8")
        encrypted_payload = RSACryptoSystem.encrypt(cvk_pub_key, payload_json)

        return {"encrypted_data": b64encode(encrypted_payload).decode("utf-8")}


class SimpleCVK(BaseCVK):
    def __init__(self, candidates: list):
        super().__init__()
        self.crypto_system = RSACryptoSystem()
        self.tallies = {candidate: 0 for candidate in candidates}
        self.log_action("CVK initialized Simple Protocol.")

    def get_public_key(self) -> bytes:
        return self.crypto_system.get_public_bytes()

    def process_vote(self, payload: Dict[str, Any]) -> bool:
        """
        3. CVK decrypts, verifies signature, checks double voting/registration, tallies.
        """
        try:
            self.log_action("Received encrypted vote payload.")
            encrypted_data = b64decode(payload.get("encrypted_data", ""))

            # Decrypt
            decrypted_json = self.crypto_system.decrypt(encrypted_data)
            self.log_action("Payload decrypted successfully with CVK private key.")

            payload_data = json.loads(decrypted_json.decode("utf-8"))

            message_bytes = b64decode(payload_data["message"])
            signature_bytes = b64decode(payload_data["signature"])
            voter_pub_key_pem = b64decode(payload_data["voter_public_key"])

            voter_pub_key = RSACryptoSystem.load_public_key(voter_pub_key_pem)

            # Verify signature
            if not RSACryptoSystem.verify(
                voter_pub_key, message_bytes, signature_bytes
            ):
                self.log_action(
                    "ERROR: Signature verification failed. Possible tampered ballot."
                )
                return False

            self.log_action("Signature verified successfully.")

            # Extract ballot
            ballot = json.loads(message_bytes.decode("utf-8"))
            voter_id = ballot.get("voter_id")
            candidate = ballot.get("candidate")

            # Check registration
            if voter_id not in self.registered_voters:
                self.log_action(
                    f"ERROR: Unregistered voter {voter_id} attempted to vote."
                )
                return False

            # Check double voting
            if voter_id in self.has_voted:
                self.log_action(f"ERROR: Voter {voter_id} attempted to vote twice.")
                return False

            # Tally vote
            if candidate not in self.tallies:
                self.log_action(
                    f"WARNING: Vote cast for unknown candidate {candidate}."
                )
                return False

            self.has_voted.add(voter_id)
            self.tallies[candidate] += 1
            self.log_action(f"Vote successfully tallied for voter {voter_id}.")
            return True

        except Exception as e:
            self.log_action(f"ERROR: Failed to process vote: {str(e)}")
            return False
