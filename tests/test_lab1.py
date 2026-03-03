import unittest

from labs.lab1.protocol import SimpleCVK, SimpleVoter


class TestLab1(unittest.TestCase):
    """
    Tests for Lab 1: Simple E-voting protocol.
    """

    def setUp(self):
        """Initialization before each test."""
        self.candidates = ["Candidate A", "Candidate B"]
        self.cvk = SimpleCVK(self.candidates)
        self.cvk.set_language("English")

        self.voter1 = SimpleVoter("voter_1")
        self.voter2 = SimpleVoter("voter_2")
        self.unregistered_voter = SimpleVoter("voter_unregistered", is_registered=False)

        self.cvk.register_voter("voter_1", self.voter1.crypto_system.get_public_bytes())
        self.cvk.register_voter("voter_2", self.voter2.crypto_system.get_public_bytes())

    def test_normal_voting(self):
        """
        Test 1: Normal voting process.
        """
        payload = self.voter1.vote("Candidate A", self.cvk.get_public_key())
        result = self.cvk.process_vote(payload, "English")

        self.assertTrue(result)
        self.assertEqual(self.cvk.tallies["Candidate A"], 1)
        self.assertIn("voter_1", self.cvk.has_voted)

    def test_double_voting(self):
        """
        Test 2 (Task 2a): Attempting to vote twice.
        """
        payload1 = self.voter1.vote("Candidate A", self.cvk.get_public_key())
        self.cvk.process_vote(payload1, "English")

        payload2 = self.voter1.vote("Candidate B", self.cvk.get_public_key())
        result = self.cvk.process_vote(payload2, "English")

        self.assertFalse(result)
        self.assertEqual(self.cvk.tallies["Candidate A"], 1)
        self.assertEqual(self.cvk.tallies["Candidate B"], 0)

    def test_unregistered_voter(self):
        """
        Test 3 (Task 2b): Voting by an unregistered voter.
        """
        payload = self.unregistered_voter.vote("Candidate A", self.cvk.get_public_key())
        result = self.cvk.process_vote(payload, "English")

        self.assertFalse(result)
        self.assertEqual(self.cvk.tallies["Candidate A"], 0)

    def test_corrupted_ballot_transmission(self):
        """
        Test 4 (Task 2c): Handling a corrupted ballot.
        """
        payload = self.voter1.vote("Candidate A", self.cvk.get_public_key())

        original_data = payload["encrypted_data"]
        corrupted_data = original_data[:-1]
        corrupted_payload = {"encrypted_data": corrupted_data}

        result = self.cvk.process_vote(corrupted_payload, "English")

        self.assertFalse(result)
        self.assertEqual(self.cvk.tallies["Candidate A"], 0)

    def test_tampered_ballot_signature(self):
        """
        Test 5: Handling a tampered ballot signature.
        """
        payload = self.voter1.vote("Candidate A", self.cvk.get_public_key(), simulate_tampering=True)
        result = self.cvk.process_vote(payload, "English")

        self.assertFalse(result)
        self.assertEqual(self.cvk.tallies["Candidate A"], 0)

    def test_tie_vote_logic(self):
        """
        Test 6 (Task 2d): Handling a tie in votes.
        """
        self.cvk.process_vote(self.voter1.vote("Candidate A", self.cvk.get_public_key()), "English")
        self.cvk.process_vote(self.voter2.vote("Candidate B", self.cvk.get_public_key()), "English")

        self.assertEqual(self.cvk.tallies["Candidate A"], 1)
        self.assertEqual(self.cvk.tallies["Candidate B"], 1)


if __name__ == '__main__':
    unittest.main()