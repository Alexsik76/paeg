import unittest

from labs.lab6.protocol import (
    RegistrationBureau,
    LowLevelCommission,
    MiddleLevelCommission,
    BlindSplitCVK,
    BlindSplitVoter
)


class TestLab6(unittest.TestCase):
    """
    Tests for Lab 6: E-voting protocol with blind signatures and split ballots.
    """

    def setUp(self):
        """Initialization before each test."""
        self.candidates = ["Candidate A", "Candidate B"]
        self.candidate_ids = {"Candidate A": 24, "Candidate B": 12}
        self.id_to_cand = {v: k for k, v in self.candidate_ids.items()}

        # Initialize Bureau of Registration (RB)
        self.rb = RegistrationBureau()

        # Initialize Central Election Commission (CVK)
        self.cvk = BlindSplitCVK(self.candidates, self.candidate_ids)
        self.cvk.set_language("English")
        self.params = self.cvk.get_public_params()

        # Initialize 4 Low-Level Commissions (LC)
        self.lcs = [LowLevelCommission(i) for i in range(4)]

        # Initialize 2 Middle-Level Commissions (MC)
        self.mcs = [
            MiddleLevelCommission(0, self.cvk.crypto_system, self.candidates, self.id_to_cand),
            MiddleLevelCommission(1, self.cvk.crypto_system, self.candidates, self.id_to_cand)
        ]

        # Initialize Voters
        self.voter1 = BlindSplitVoter("voter_1")
        self.voter2 = BlindSplitVoter("voter_2")
        self.unregistered_voter = BlindSplitVoter("voter_unregistered", is_registered=False)

        # Register voters
        self.cvk.register_voter("voter_1")
        self.cvk.register_voter("voter_2")
        self.rb.register("voter_1")
        self.rb.register("voter_2")

    def test_full_successful_voting_flow(self):
        """
        Test 1: Normal voting process across all levels of commissions.
        """
        cand_id = self.candidate_ids["Candidate A"]

        # 1. Voter prepares and blinds parts
        blinded_parts = self.voter1.prepare_vote(cand_id, self.params['n'], self.params['e'])

        # 2. CVK signs blinded parts
        signed_blinded = self.cvk.sign_blind_parts(self.voter1.voter_id, blinded_parts)
        self.assertIsNotNone(signed_blinded)

        # 3. Voter unblinds signatures
        sigs = self.voter1.unblind_signatures(signed_blinded if signed_blinded is not None else (0, 0), self.params['n'])

        # 4. LCs process parts and verify signatures
        res1 = self.lcs[0].process_partial(self.voter1.anonymous_id, self.voter1.parts[0], sigs[0], self.params)
        res2 = self.lcs[1].process_partial(self.voter1.anonymous_id, self.voter1.parts[1], sigs[1], self.params)
        self.assertTrue(res1)
        self.assertTrue(res2)

        # 5. MC aggregates, decrypts, and tallies
        self.mcs[0].aggregate_and_count(self.lcs[0], self.lcs[1], self.params['n'], "English")
        self.assertEqual(self.mcs[0].tallies["Candidate A"], 1)

        # 6. CVK aggregates results from all MCs
        self.cvk.aggregate_mc_results(self.mcs)
        self.assertEqual(self.cvk.tallies["Candidate A"], 1)

    def test_unregistered_voter_signature_denial(self):
        """
        Test 2: CVK refuses to sign parts for an unregistered voter.
        """
        cand_id = self.candidate_ids["Candidate A"]
        blinded_parts = self.unregistered_voter.prepare_vote(cand_id, self.params['n'], self.params['e'])

        signed_blinded = self.cvk.sign_blind_parts(self.unregistered_voter.voter_id, blinded_parts)
        
        self.assertIsNone(signed_blinded)

    def test_double_signature_request_prevention(self):
        """
        Test 3: Voter cannot get a second set of signatures from CVK.
        """
        cand_id = self.candidate_ids["Candidate A"]
        blinded_parts = self.voter1.prepare_vote(cand_id, self.params['n'], self.params['e'])

        # First signature request
        signed_1 = self.cvk.sign_blind_parts(self.voter1.voter_id, blinded_parts)
        self.assertIsNotNone(signed_1)

        # Second signature request with the same voter ID
        signed_2 = self.cvk.sign_blind_parts(self.voter1.voter_id, blinded_parts)
        self.assertIsNone(signed_2)

    def test_tampered_signature_rejection_at_lc(self):
        """
        Test 4: LC rejects a ballot part with an invalid (tampered) signature.
        """
        cand_id = self.candidate_ids["Candidate A"]
        blinded_parts = self.voter1.prepare_vote(cand_id, self.params['n'], self.params['e'])
        signed_blinded = self.cvk.sign_blind_parts(self.voter1.voter_id, blinded_parts)
        sigs = list(self.voter1.unblind_signatures(signed_blinded if signed_blinded is not None else (0, 0), self.params['n']))

        # Tamper with the signature
        tampered_sig = (sigs[0] + 1) % self.params['n']

        res = self.lcs[0].process_partial(self.voter1.anonymous_id, self.voter1.parts[0], tampered_sig, self.params)
        self.assertFalse(res)
        self.assertNotIn(self.voter1.anonymous_id, self.lcs[0].partial_ballots)

    def test_tampered_part_content_rejection_at_lc(self):
        """
        Test 5: LC rejects a ballot if the content (part) doesn't match the valid signature.
        """
        cand_id = self.candidate_ids["Candidate A"]
        blinded_parts = self.voter1.prepare_vote(cand_id, self.params['n'], self.params['e'])
        signed_blinded = self.cvk.sign_blind_parts(self.voter1.voter_id, blinded_parts)
        sigs = self.voter1.unblind_signatures(signed_blinded if signed_blinded is not None else (0, 0), self.params['n'])

        # Tamper with the ballot part
        tampered_part = (self.voter1.parts[0] + 1) % self.params['n']

        res = self.lcs[0].process_partial(self.voter1.anonymous_id, tampered_part, sigs[0], self.params)
        self.assertFalse(res)

    def test_mc_double_counting_prevention(self):
        """
        Test 6: MC prevents recounting the same anonymous ID.
        """
        cand_id = self.candidate_ids["Candidate A"]
        blinded_parts = self.voter1.prepare_vote(cand_id, self.params['n'], self.params['e'])
        signed_blinded = self.cvk.sign_blind_parts(self.voter1.voter_id, blinded_parts)
        sigs = self.voter1.unblind_signatures(signed_blinded if signed_blinded is not None else (0, 0), self.params['n'])

        self.lcs[0].process_partial(self.voter1.anonymous_id, self.voter1.parts[0], sigs[0], self.params)
        self.lcs[1].process_partial(self.voter1.anonymous_id, self.voter1.parts[1], sigs[1], self.params)

        # First aggregation
        self.mcs[0].aggregate_and_count(self.lcs[0], self.lcs[1], self.params['n'], "English")
        self.assertEqual(self.mcs[0].tallies["Candidate A"], 1)

        # Attempted second aggregation for the same LCs data
        self.mcs[0].aggregate_and_count(self.lcs[0], self.lcs[1], self.params['n'], "English")
        self.assertEqual(self.mcs[0].tallies["Candidate A"], 1)


if __name__ == '__main__':
    unittest.main()