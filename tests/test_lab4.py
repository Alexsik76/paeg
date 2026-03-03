import unittest
import base64

from labs.lab4.protocol import VotingCommission, SplitFactorCVK, SplitFactorVoter


class TestLab4(unittest.TestCase):
    """
    Tests for Lab 4: E-voting protocol with split authorities and homomorphic encryption.
    """

    def setUp(self):
        """Initialization before each test."""
        self.candidates = ["Candidate A", "Candidate B"]
        self.candidate_id_map = {"Candidate A": 24, "Candidate B": 12}
        
        # Initialize Voting Commissions
        self.vc1 = VotingCommission(1)
        self.vc2 = VotingCommission(2)
        
        # Initialize CVK
        self.cvk = SplitFactorCVK(self.candidates, self.candidate_id_map)
        self.cvk.set_language("English")
        self.key_params = self.cvk.get_key_params()

        # Initialize Voter
        self.voter1 = SplitFactorVoter("voter_1")
        self.voter2 = SplitFactorVoter("voter_2")

    def test_normal_voting_flow_and_homomorphic_join(self):
        """
        Test 1 (Task 2d): Normal flow proving that joining happens before decryption.
        """
        cand_val = self.candidate_id_map["Candidate A"]
        p1, p2, f1, f2 = self.voter1.vote(cand_val, self.key_params)

        # Both VCs must accept the valid partial ballots
        self.assertTrue(self.vc1.process_partial_ballot(p1, "English"))
        self.assertTrue(self.vc2.process_partial_ballot(p2, "English"))

        # CVK joins factors homomorphically and tallies
        self.cvk.process_and_tally(
            self.vc1.get_partial_ballots(), 
            self.vc2.get_partial_ballots(), 
            "English"
        )

        self.assertEqual(self.cvk.tallies["Candidate A"], 1)

    def test_invalid_signature_detection(self):
        """
        Test 2 (Task 2a): VCs detect invalid ballots via signature verification.
        """
        cand_val = self.candidate_id_map["Candidate A"]
        p1, p2, _, _ = self.voter1.vote(cand_val, self.key_params)

        # Corrupt the signature in payload 1
        corrupted_signature_bytes = base64.b64decode(p1["signature"])[:-1]
        p1["signature"] = base64.b64encode(corrupted_signature_bytes).decode("utf-8")

        # VC1 should reject the corrupted partial ballot
        result = self.vc1.process_partial_ballot(p1, "English")
        self.assertFalse(result)
        self.assertNotIn(self.voter1.anonymous_id, self.vc1.partial_ballots)

    def test_tampered_partial_ballot_detection(self):
        """
        Test 3 (Task 2b): Tampering by a VC is detected during CVK decryption.
        """
        cand_val = self.candidate_id_map["Candidate A"]
        p1, p2, _, _ = self.voter1.vote(cand_val, self.key_params)

        self.vc1.process_partial_ballot(p1, "English")
        self.vc2.process_partial_ballot(p2, "English")

        # VC-1 tamperes with the stored encrypted factor
        anon_id = self.voter1.anonymous_id
        original_factor = self.vc1.partial_ballots[anon_id]
        self.vc1.partial_ballots[anon_id] = (original_factor * 7) % self.key_params["n"]

        # CVK attempts to process tampered data
        self.cvk.process_and_tally(
            self.vc1.get_partial_ballots(), 
            self.vc2.get_partial_ballots(), 
            "English"
        )

        # The decrypted value will be garbage, not matching any candidate ID
        self.assertEqual(self.cvk.tallies["Candidate A"], 0)
        self.assertEqual(self.cvk.tallies["Candidate B"], 0)

    def test_arbitrary_factor_splitting(self):
        """
        Test 4 (Task 2c): Verify that the random factor splitting works correctly.
        """
        cand_val = self.candidate_id_map["Candidate A"]
        n = self.key_params["n"]
        
        f1, f2 = self.voter1.split_id(cand_val, n)
        
        # Prove that the modular multiplication of factors restores the candidate ID
        restored_val = (f1 * f2) % n
        self.assertEqual(restored_val, cand_val)

    def test_double_voting_prevention(self):
        """
        Test 5: A VC must reject a second partial ballot from the same public key.
        """
        cand_val = self.candidate_id_map["Candidate A"]
        p1, p2, _, _ = self.voter1.vote(cand_val, self.key_params)

        # First submission should be successful
        self.assertTrue(self.vc1.process_partial_ballot(p1, "English"))

        # Second submission from the same voter (same public key) must be rejected
        self.assertFalse(self.vc1.process_partial_ballot(p1, "English"))


if __name__ == '__main__':
    unittest.main()