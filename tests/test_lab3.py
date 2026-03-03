import unittest
import uuid

from labs.lab3.protocol import RegistrationBureau, SplitCVK, SplitVoter


class TestLab3(unittest.TestCase):
    """
    Tests for Lab 3: E-voting protocol with split authorities (BR and CVK).
    """

    def setUp(self):
        """Initialization before each test."""
        self.candidates = ["Candidate A", "Candidate B"]
        
        # Initialize Bureau of Registration (BR)
        self.br = RegistrationBureau()
        
        # Initialize Central Election Commission (CVK)
        self.cvk = SplitCVK(self.candidates)
        self.cvk.set_language("English")
        self.cvk_pub_pem = self.cvk.get_public_key()

        # Initialize Voters
        self.voter1 = SplitVoter("voter_1")
        self.voter2 = SplitVoter("voter_2")

    def test_normal_voting_flow(self):
        """
        Test 1: Normal voting process with RN issuance and successful tally.
        """
        rn = self.br.register_voter(self.voter1.voter_id, "English")
        self.assertIsNotNone(rn)
        assert rn is not None  # narrow type for static type checkers
        
        self.voter1.set_rn(rn)
        self.cvk.load_rns_from_br(self.br.get_valid_rns())

        payload = self.voter1.vote("Candidate A", self.cvk_pub_pem)
        result = self.cvk.process_vote(payload, "English")

        self.assertTrue(result)
        self.assertEqual(self.cvk.tallies["Candidate A"], 1)

    def test_double_rn_request(self):
        """
        Test 2 (Task 2a): Voter cannot get more than one RN from BR.
        """
        rn1 = self.br.register_voter(self.voter1.voter_id, "English")
        self.assertIsNotNone(rn1)

        # Attempt to request a second RN for the same voter ID
        rn2 = self.br.register_voter(self.voter1.voter_id, "English")
        self.assertIsNone(rn2)

    def test_double_voting_rejection(self):
        """
        Test 3 (Task 2b): Voter cannot vote twice using the same RN.
        """
        rn = self.br.register_voter(self.voter1.voter_id, "English")
        self.assertIsNotNone(rn)
        assert rn is not None
        
        self.voter1.set_rn(rn)
        self.cvk.load_rns_from_br(self.br.get_valid_rns())

        # First vote
        payload1 = self.voter1.vote("Candidate A", self.cvk_pub_pem)
        result1 = self.cvk.process_vote(payload1, "English")
        self.assertTrue(result1)

        # Second vote attempt with the same RN
        payload2 = self.voter1.vote("Candidate B", self.cvk_pub_pem)
        result2 = self.cvk.process_vote(payload2, "English")

        self.assertFalse(result2)
        self.assertEqual(self.cvk.tallies["Candidate A"], 1)
        self.assertEqual(self.cvk.tallies["Candidate B"], 0)

    def test_invalid_rn_rejection(self):
        """
        Test 4 (Task 2b): Voting with an invalid (fake) RN is rejected.
        """
        fake_rn = str(uuid.uuid4())
        self.voter1.set_rn(fake_rn)
        
        # BR sends valid RNs to CVK (empty in this case, as no one registered properly)
        self.cvk.load_rns_from_br(self.br.get_valid_rns())

        payload = self.voter1.vote("Candidate A", self.cvk_pub_pem)
        result = self.cvk.process_vote(payload, "English")

        self.assertFalse(result)
        self.assertEqual(self.cvk.tallies["Candidate A"], 0)

    def test_vote_verification(self):
        """
        Test 5 (Task 2c): Voter can verify their vote in the published results.
        """
        rn = self.br.register_voter(self.voter1.voter_id, "English")
        self.assertIsNotNone(rn)
        assert rn is not None
        self.voter1.set_rn(rn)
        self.cvk.load_rns_from_br(self.br.get_valid_rns())

        payload = self.voter1.vote("Candidate A", self.cvk_pub_pem)
        self.cvk.process_vote(payload, "English")

        # Voter checks CVK's published ballots using their anonymous ID
        anon_id = self.voter1.anonymous_id
        
        self.assertIn(anon_id, self.cvk.published_ballots)
        self.assertEqual(self.cvk.published_ballots[anon_id]["candidate"], "Candidate A")

    def test_voting_without_rn_raises_error(self):
        """
        Test 6: Voter attempts to prepare a ballot without an RN.
        """
        # Voter did not call br.register_voter() and has no RN
        with self.assertRaises(ValueError):
            self.voter1.vote("Candidate A", self.cvk_pub_pem)


if __name__ == '__main__':
    unittest.main()