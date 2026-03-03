import unittest

from labs.lab2.protocol import BlindCVK, BlindVoter


class TestLab2(unittest.TestCase):
    """
    Tests for Lab 2: E-voting protocol with blind signatures (RSA).
    """

    def setUp(self):
        """Initialization before each test."""
        self.candidates = ["Candidate A", "Candidate B"]
        self.cvk = BlindCVK(self.candidates)
        self.cvk.set_language("English")
        
        self.cvk_e, self.cvk_n = self.cvk.get_public_numbers()
        self.cvk_pub_pem = self.cvk.get_public_key()

        self.voter1 = BlindVoter("voter_1")
        self.voter2 = BlindVoter("voter_2")
        self.unregistered_voter = BlindVoter("voter_unregistered", is_registered=False)

        self.cvk.register_voter("voter_1", self.voter1.crypto_system.get_public_bytes())
        self.cvk.register_voter("voter_2", self.voter2.crypto_system.get_public_bytes())

    def _perform_successful_sign_step(self, voter: BlindVoter):
        """Helper method to execute the complex 9/10 verification and signing process."""
        blinded_sets = voter.prepare_blinded_sets(self.cvk_e, self.cvk_n, self.candidates)
        chosen_idx, checked_indices = self.cvk.choose_sets_to_check()
        multipliers = voter.provide_multipliers(checked_indices)
        
        signed_set = self.cvk.verify_and_sign(
            voter.voter_id, blinded_sets, checked_indices, multipliers, chosen_idx, "English"
        )
        return signed_set, chosen_idx

    def test_normal_blind_voting(self):
        """
        Test 1: Normal blind voting process.
        """
        signed_set, chosen_idx = self._perform_successful_sign_step(self.voter1)
        
        self.assertTrue(signed_set)
        
        self.voter1.process_signed_set(signed_set, chosen_idx, self.cvk_n)
        payload = self.voter1.vote("Candidate A", self.cvk_pub_pem)
        
        result = self.cvk.process_vote(payload, "English")
        
        self.assertTrue(result)
        self.assertEqual(self.cvk.tallies["Candidate A"], 1)

    def test_double_signature_request(self):
        """
        Test 2 (Task 2a): Attempting to get a second set of ballots signed.
        """
        signed_set_1, _ = self._perform_successful_sign_step(self.voter1)
        self.assertTrue(signed_set_1)

        signed_set_2, _ = self._perform_successful_sign_step(self.voter1)
        self.assertFalse(signed_set_2)

    def test_double_voting_with_signed_ballots(self):
        """
        Test 3 (Task 2b): Attempting to send both signed ballots to CVK.
        """
        signed_set, chosen_idx = self._perform_successful_sign_step(self.voter1)
        self.voter1.process_signed_set(signed_set, chosen_idx, self.cvk_n)

        payload1 = self.voter1.vote("Candidate A", self.cvk_pub_pem)
        result1 = self.cvk.process_vote(payload1, "English")
        self.assertTrue(result1)

        payload2 = self.voter1.vote("Candidate B", self.cvk_pub_pem)
        result2 = self.cvk.process_vote(payload2, "English")
        
        self.assertFalse(result2)
        self.assertEqual(self.cvk.tallies["Candidate A"], 1)
        self.assertEqual(self.cvk.tallies["Candidate B"], 0)

    def test_fraudulent_sets_detection(self):
        """
        Test 4 (Task 2c): Detection of tampered ballot in the 9/10 check.
        """
        blinded_sets = self.voter1.prepare_blinded_sets(self.cvk_e, self.cvk_n, self.candidates)
        chosen_idx, checked_indices = self.cvk.choose_sets_to_check()
        
        tampered_idx = checked_indices[0]
        self.voter1.multipliers[tampered_idx]["Candidate A"] += 1
        
        multipliers = self.voter1.provide_multipliers(checked_indices)
        signed_set = self.cvk.verify_and_sign(
            self.voter1.voter_id, blinded_sets, checked_indices, multipliers, chosen_idx, "English"
        )
        
        self.assertFalse(signed_set)

    def test_unregistered_voter_signature_request(self):
        """
        Test 5: Attempting to get signatures by an unregistered voter.
        """
        blinded_sets = self.unregistered_voter.prepare_blinded_sets(self.cvk_e, self.cvk_n, self.candidates)
        chosen_idx, checked_indices = self.cvk.choose_sets_to_check()
        multipliers = self.unregistered_voter.provide_multipliers(checked_indices)
        
        signed_set = self.cvk.verify_and_sign(
            self.unregistered_voter.voter_id, blinded_sets, checked_indices, multipliers, chosen_idx, "English"
        )
        
        self.assertFalse(signed_set)


if __name__ == '__main__':
    unittest.main()