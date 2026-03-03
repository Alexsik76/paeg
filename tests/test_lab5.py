import unittest
from base64 import b64encode

from labs.lab5.protocol import DecentralizedVoter


class TestLab5(unittest.TestCase):
    """
    Tests for Lab 5: Decentralized E-voting protocol without a commission.
    """

    def setUp(self):
        """Initialization before each test."""
        # Initialize 5 voters as required by the task
        self.voters = [
            DecentralizedVoter(f"voter_{i}") for i in range(1, 6)
        ]
        self.candidate_id = "24" 

    def test_normal_decentralized_voting_flow(self):
        """
        Test 1: Normal full protocol flow with 5 voters and 2 rounds of decryption.
        """
        encrypted_ballots = []

        # Phase 1: All voters prepare their layered encrypted ballots
        for voter in self.voters:
            voter.voted = True
            ballot = voter.prepare_ballot(self.candidate_id, self.voters)
            encrypted_ballots.append(ballot)

        current_ballots = encrypted_ballots

        # Phase 2: Decryption Rounds (2 rounds as per theoretical material)
        for round_num in range(2):
            prev_sig = None
            prev_pub_key = None

            for voter in self.voters:
                # Each voter decrypts their layer, checks their RP, and shuffles
                current_ballots = voter.process_round(current_ballots, prev_sig, prev_pub_key)
                
                # Sign the output for the next voter in the sequence
                signature = voter.sign_ballots(current_ballots)
                prev_sig = b64encode(signature).decode("utf-8")
                prev_pub_key = voter.crypto_system.get_public_bytes()

        # Phase 3: Final Tally Verification
        # After 2 rounds, all layers are removed, revealing the inner candidate IDs
        for ballot in current_ballots:
            self.assertEqual(ballot, self.candidate_id)

    def test_tampered_ballot_detection(self):
        """
        Test 2 (Task 2a): Detection of a tampered ballot during decryption.
        """
        voter1 = self.voters[0]
        voter1.voted = True
        ballot = voter1.prepare_ballot(self.candidate_id, self.voters)
        
        # Tamper with the ballot's ciphertext structure
        tampered_ballot = ballot[:-4] + "AAAA"
        
        # The first voter to process it should fail to decrypt the tampered data
        with self.assertRaises(ValueError) as context:
            voter1.process_round([tampered_ballot])
        
        self.assertEqual(str(context.exception), "DECRYPTION_FAILED")

    def test_missing_ballot_rp_detection(self):
        """
        Test 3 (Task 2b): Detection of a removed ballot (RP missing).
        """
        voter1 = self.voters[0]
        voter2 = self.voters[1]
        
        voter1.voted = True
        voter2.voted = True
        
        ballot2 = voter2.prepare_ballot(self.candidate_id, self.voters)
        
        # Simulate ballot1 being removed by a malicious actor
        current_ballots = [ballot2]
        
        # When voter1 tries to process the round, they will notice their RP is gone
        with self.assertRaises(ValueError) as context:
            voter1.process_round(current_ballots)
            
        self.assertEqual(str(context.exception), "RP_NOT_FOUND")

    def test_signature_mismatch_detection(self):
        """
        Test 4: Detection of invalid signature from the previous voter.
        """
        voter1 = self.voters[0]
        voter2 = self.voters[1]
        
        ballot = voter1.prepare_ballot(self.candidate_id, self.voters)
        
        # Voter 1 processes and signs the data
        processed_ballots = voter1.process_round([ballot])
        valid_signature = voter1.sign_ballots(processed_ballots)
        
        # Simulate a Man-in-the-Middle tampering with the signature bytes
        tampered_signature = b64encode(valid_signature[:-1] + b'X').decode("utf-8")
        pub_key = voter1.crypto_system.get_public_bytes()
        
        # Voter 2 must reject the payload due to signature mismatch
        with self.assertRaises(ValueError) as context:
            voter2.process_round(processed_ballots, tampered_signature, pub_key)
            
        self.assertEqual(str(context.exception), "SIGNATURE_MISMATCH")


if __name__ == '__main__':
    unittest.main()