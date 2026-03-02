from typing import Dict, List
import random
import time

from labs.base import BaseScenarioRunner
from labs.lab6.protocol import (
    BlindSplitVoter,
    RegistrationBureau,
    LowLevelCommission,
    MiddleLevelCommission,
    BlindSplitCVK,
)
from core.i18n import t, T


class Lab6ScenarioRunner(BaseScenarioRunner):
    def __init__(
        self,
        cvk: BlindSplitCVK,
        rb: RegistrationBureau,
        mcs: List[MiddleLevelCommission],
        lcs: List[LowLevelCommission],
        voters: Dict[str, BlindSplitVoter],
        candidates: List[str],
        lang: str,
        candidate_ids: Dict[str, int],
        visualizer=None,
        graph_placeholder=None,
        animation_delay: float = 1.0,
    ):
        super().__init__(voters, candidates, lang)
        self.cvk = cvk
        self.rb = rb
        self.mcs = mcs
        self.lcs = lcs
        self.candidate_ids = candidate_ids
        self.visualizer = visualizer
        self.graph_placeholder = graph_placeholder
        self.animation_delay = animation_delay
        # Mapping: MC1 uses LC1 & LC2. MC2 uses LC3 & LC4.
        self.mc_lc_map = {0: [0, 1], 1: [2, 3]}
        self.logs = []

    def reset_election(self):
        """Clears logs and resets state for a fresh simulation run."""
        self.logs = []
        # Clear LCs
        for lc in self.lcs:
            lc.partial_ballots.clear()
        # Clear MCs
        for mc in self.mcs:
            for cand in mc.candidates:
                mc.tallies[cand] = 0
            mc.voted_anon_ids.clear()
        # Reset CVK tallies (but don't clear registration)
        for cand in self.cvk.candidates:
            self.cvk.tallies[cand] = 0
        self.cvk.voters_signed.clear()
        if self.visualizer and self.graph_placeholder:
            self.visualizer.clear_all()
            self.visualizer.render(self.graph_placeholder)

    def log(self, message: str):
        self.logs.append(message)

    def run(
        self, scenario_id: str, selected_voter_id: str, selected_candidate: str
    ) -> List[str]:
        self.reset_election()

        # Pre-register all voters at CVK (as per base classes behavior)
        for vid in self.voters:
            self.cvk.register_voter(vid)
            self.rb.register(vid)

        if scenario_id == "scenario_normal_lab6":
            return self.run_normal(selected_voter_id, selected_candidate)
        elif scenario_id == "scenario_simulate_all_lab6":
            return self.run_simulate_all()
        elif scenario_id == "scenario_double_vote_lab6":
            return self.run_double_vote(selected_voter_id, selected_candidate)
        elif scenario_id == "scenario_tamper_lab6":
            return self.run_tamper(selected_voter_id, selected_candidate)

        return ["Unknown scenario"]

    def _execute_vote_flow(
        self,
        voter_id: str,
        candidate_name: str,
        mc_index: int = 0,
        show_animation: bool = True,
    ) -> bool:
        voter = self.voters[voter_id]
        cand_id = self.candidate_ids[candidate_name]
        params = self.cvk.get_public_params()
        n, e = params["n"], params["e"]

        self.log("--- Voter " + voter_id + " starts voting ---")

        # 1. Registration Check
        if self.visualizer and show_animation and self.graph_placeholder:
            # Step A: Request
            self.log(t(T.LAB6_REQ_REG, self.lang))
            self.visualizer.activate_flow("e_reg", t(T.LAB6_REQ_REG, self.lang))
            self.visualizer.render(self.graph_placeholder)
            time.sleep(self.animation_delay)
            self.visualizer.deactivate_all_flows()
            # Step B: Response
            self.visualizer.activate_flow(
                "e_rb_v", t(T.LAB6_BR_VERIFIED, self.lang, voter=voter_id)
            )
            self.visualizer.render(self.graph_placeholder)
            time.sleep(self.animation_delay)
            self.visualizer.deactivate_all_flows()

        if not self.rb.is_registered(voter_id):
            self.log(t(T.ERR_UNREGISTERED, self.lang, voter=voter_id))
            return False
        self.log(t(T.LAB6_BR_VERIFIED, self.lang, voter=voter_id))

        # 2. Prepare Blinded Parts
        if self.visualizer and show_animation and self.graph_placeholder:
            self.log(t(T.LAB6_VOTER_PREPARING, self.lang))
            self.visualizer.active_node = "voter"
            self.visualizer.message = t(T.LAB6_VOTER_PREPARING, self.lang)
            self.visualizer.render(self.graph_placeholder)
            time.sleep(self.animation_delay)
            self.visualizer.deactivate_all_flows()

        blinded_parts = voter.prepare_vote(cand_id, n, e)
        self.log(t(T.LAB6_VOTER_PREPARED_PARTS, self.lang))

        # 3. Get Blind Signatures from CVK
        if self.visualizer and show_animation and self.graph_placeholder:
            # Step A: Request
            self.log(t(T.LAB6_REQ_SIGN, self.lang))
            self.visualizer.activate_flow("e_blind", t(T.LAB6_REQ_SIGN, self.lang))
            self.visualizer.render(self.graph_placeholder)
            time.sleep(self.animation_delay)
            self.visualizer.deactivate_all_flows()
            # Step B: Response
            self.visualizer.activate_flow(
                "e_cec_v", t(T.LAB6_CVK_SIGNED_PARTS, self.lang, voter=voter_id)
            )
            self.visualizer.render(self.graph_placeholder)
            time.sleep(self.animation_delay)
            self.visualizer.deactivate_all_flows()

        signed_blinded = self.cvk.sign_blind_parts(voter_id, blinded_parts)
        if not signed_blinded:
            self.log(t(T.LAB6_CVK_DENIED_SIGNATURE, self.lang, voter=voter_id))
            return False

        self.log(t(T.LAB6_CVK_SIGNED_PARTS, self.lang, voter=voter_id))

        # 4. Unblind
        if self.visualizer and show_animation and self.graph_placeholder:
            self.log(t(T.LAB6_VOTER_UNBLINDING, self.lang))
            self.visualizer.active_node = "voter"
            self.visualizer.message = t(T.LAB6_VOTER_UNBLINDING, self.lang)
            self.visualizer.render(self.graph_placeholder)
            time.sleep(self.animation_delay)
            self.visualizer.deactivate_all_flows()

        unblinded_sigs = voter.unblind_signatures(signed_blinded, n)
        self.log(t(T.LAB6_VOTER_UNBLINDED, self.lang))

        # 5. Send to LCs
        if self.visualizer and show_animation and self.graph_placeholder:
            lc_indices = self.mc_lc_map[mc_index]
            self.visualizer.activate_flow(
                f"e_v{mc_index + 1}_lc{lc_indices[0] + 1}",
                t(T.LAB6_VOTER_PREPARED_PARTS, self.lang),
            )
            self.visualizer.activate_flow(
                f"e_v{mc_index + 1}_lc{lc_indices[1] + 1}",
                t(T.LAB6_VOTER_PREPARED_PARTS, self.lang),
            )
            self.visualizer.render(self.graph_placeholder)
            time.sleep(self.animation_delay)
            self.visualizer.deactivate_all_flows()

        lc_indices = self.mc_lc_map[mc_index]
        lc1 = self.lcs[lc_indices[0]]
        lc2 = self.lcs[lc_indices[1]]

        res1 = lc1.process_partial(
            voter.anonymous_id, voter.parts[0], unblinded_sigs[0], params
        )
        res2 = lc2.process_partial(
            voter.anonymous_id, voter.parts[1], unblinded_sigs[1], params
        )

        if res1 and res2:
            self.log(
                t(T.LAB6_LCS_PARTS_ACCEPTED, self.lang, anon_id=voter.anonymous_id[:8])
            )
            return True
        else:
            self.log(
                t(T.LAB6_LCS_PARTS_REJECTED, self.lang, anon_id=voter.anonymous_id[:8])
            )
            return False

    def run_normal(self, voter_id: str, candidate_name: str) -> List[str]:
        success = self._execute_vote_flow(voter_id, candidate_name, mc_index=0)

        if success:
            # Aggregate at MC
            mc = self.mcs[0]
            if self.visualizer and self.graph_placeholder:
                self.log(t(T.LAB6_AGGREGATING, self.lang))
                self.visualizer.activate_flow(
                    "e_lc1_mc1", t(T.LAB6_AGGREGATING, self.lang)
                )
                self.visualizer.activate_flow(
                    "e_lc2_mc1", t(T.LAB6_AGGREGATING, self.lang)
                )
                self.visualizer.render(self.graph_placeholder)
                time.sleep(self.animation_delay)
                self.visualizer.deactivate_all_flows()

            mc_logs = mc.aggregate_and_count(
                self.lcs[0], self.lcs[1], self.cvk.n, self.lang
            )
            if mc_logs:
                # Need to manually format MC logs since they come from protocol.py
                # Actually I should update protocol.py too, but for now I'll just append
                self.logs.extend(mc_logs)
                if self.visualizer and self.graph_placeholder:
                    self.log(t(T.LAB6_SENDING_TO_CEC, self.lang))
                    self.visualizer.activate_flow(
                        "e_mc1_cec", t(T.LAB6_SENDING_TO_CEC, self.lang)
                    )
                    self.visualizer.render(self.graph_placeholder)
                    time.sleep(self.animation_delay)
                    self.visualizer.deactivate_all_flows()
            else:
                self.log(t(T.LAB6_MC_NO_BALLOTS, self.lang, id=mc.commission_id))

            # Final CEC tally
            if self.visualizer and self.graph_placeholder:
                self.log(t(T.LAB6_CEC_TALLYING, self.lang))
                self.visualizer.active_node = "cec"
                self.visualizer.message = t(T.LAB6_CEC_TALLYING, self.lang)
                self.visualizer.render(self.graph_placeholder)
                time.sleep(self.animation_delay)
                self.visualizer.deactivate_all_flows()

            self.cvk.aggregate_mc_results(self.mcs)

            # RESULTS UPDATED stage
            res_msg = t(
                T.LAB6_CEC_FINAL_TALLY,
                self.lang,
                candidate=candidate_name,
                count=self.cvk.tallies[candidate_name],
            )
            self.log(res_msg)
            if self.visualizer and self.graph_placeholder:
                self.visualizer.message = res_msg
                self.visualizer.render(self.graph_placeholder)
                time.sleep(self.animation_delay)

            # FINAL SUCCESS stage
            final_msg = f"{t(T.VOTING_COMPLETED, self.lang)}\n{t(T.VOTE_TALLIED, self.lang, voter=voter_id)}"
            self.log(final_msg)
            if self.visualizer and self.graph_placeholder:
                self.visualizer.deactivate_all_flows()
                self.visualizer.is_final = True
                self.visualizer.message = final_msg
                self.visualizer.render(self.graph_placeholder)
                # DO NOT deactivate_all_flows so it stays

        return self.logs

    def run_simulate_all(self) -> List[str]:
        for i, (vid, voter) in enumerate(self.voters.items()):
            # Distribute voters between MC1 and MC2
            mc_idx = i % 2
            cand = random.choice(self.candidates)
            # Skip animation for full simulation to save time
            self._execute_vote_flow(vid, cand, mc_idx, show_animation=False)

        self.log("--- End of voting phase. Starting aggregation ---")

        # All MCs aggregate
        for i, mc in enumerate(self.mcs):
            lc_indices = self.mc_lc_map[i]
            if self.visualizer and self.graph_placeholder:
                self.log(t(T.LAB6_AGGREGATING, self.lang))
                id1, id2 = lc_indices[0] + 1, lc_indices[1] + 1
                self.visualizer.activate_flow(
                    f"e_lc{id1}_mc{i + 1}", t(T.LAB6_AGGREGATING, self.lang)
                )
                self.visualizer.activate_flow(
                    f"e_lc{id2}_mc{i + 1}", t(T.LAB6_AGGREGATING, self.lang)
                )
                self.visualizer.render(self.graph_placeholder)
                time.sleep(self.animation_delay)
                self.visualizer.deactivate_all_flows()

            mc_logs = mc.aggregate_and_count(
                self.lcs[lc_indices[0]],
                self.lcs[lc_indices[1]],
                self.cvk.n,
                self.lang,
            )
            self.logs.extend(mc_logs)
            if self.visualizer and mc_logs and self.graph_placeholder:
                self.log(t(T.LAB6_SENDING_TO_CEC, self.lang))
                self.visualizer.activate_flow(
                    f"e_mc{i + 1}_cec", t(T.LAB6_SENDING_TO_CEC, self.lang)
                )
                self.visualizer.render(self.graph_placeholder)
                time.sleep(self.animation_delay)
                self.visualizer.deactivate_all_flows()

        self.cvk.aggregate_mc_results(self.mcs)
        if self.visualizer and self.graph_placeholder:
            self.log(t(T.LAB6_CEC_TALLYING, self.lang))
            self.visualizer.active_node = "cec"
            self.visualizer.message = t(T.LAB6_CEC_TALLYING, self.lang)
            self.visualizer.render(self.graph_placeholder)
            time.sleep(self.animation_delay)
            self.visualizer.deactivate_all_flows()

        self.log("--- FINAL RESULTS ---")
        for cand, count in self.cvk.tallies.items():
            self.log(cand + ": " + str(count))

        # Check total votes vs registered
        total_votes = sum(self.cvk.tallies.values())
        total_registered = len(self.voters)

        if total_votes == total_registered:
            status_msg = t(T.SIMULATION_OK, self.lang, count=total_votes)
        else:
            status_msg = t(
                T.SIMULATION_ERRORS,
                self.lang,
                success_count=total_votes,
                total_count=total_registered,
            )

        self.log(status_msg)
        if self.visualizer and self.graph_placeholder:
            final_summary = f"{t(T.VOTING_COMPLETED, self.lang)}\n{status_msg}"
            self.visualizer.deactivate_all_flows()
            self.visualizer.is_final = True
            self.visualizer.message = final_summary
            self.visualizer.render(self.graph_placeholder)
            # Persist last message

        return self.logs

    def run_double_vote(self, voter_id: str, candidate_name: str) -> List[str]:
        self.log(f"Attempting double voting for {voter_id}...")

        # First legitimate vote
        self._execute_vote_flow(voter_id, candidate_name, mc_index=0)

        # Second attempt (same voter ID, new anonymous ID)
        self.log("--- Second attempt with same Voter ID ---")
        # Reset voter's anonymous ID to simulate a fresh attempt
        import uuid

        old_anon_id = self.voters[voter_id].anonymous_id
        self.voters[voter_id].anonymous_id = str(uuid.uuid4())

        success2 = self._execute_vote_flow(voter_id, candidate_name, mc_index=0)
        if not success2:
            self.log(t(T.ERR_DOUBLE_VOTE, self.lang, voter=voter_id))

        # Third attempt (manual injection of existing signed part - double anon ID)
        self.log("--- Attempting to reuse already signed parts ---")
        mc = self.mcs[0]
        mc_logs = mc.aggregate_and_count(
            self.lcs[0], self.lcs[1], self.cvk.n, self.lang
        )
        if mc_logs:
            self.logs.extend(mc_logs)
        self.log("First aggregation successful.")

        # Try to aggregate again (MC should prevent reuse)
        self.log("Second aggregation attempt for same anon ID...")
        mc_logs2 = mc.aggregate_and_count(
            self.lcs[0], self.lcs[1], self.cvk.n, self.lang
        )
        if not mc_logs2:
            # Use a generic error for duplicate anon ID to show red banner
            self.log(t(T.LAB6_MC_DUPLICATE_ANON, self.lang, anon_id=old_anon_id[:8]))
        else:
            self.logs.extend(mc_logs2)
            self.log("ERROR: MC allowed duplicate processing of anonymous ID!")

        return self.logs

    def run_tamper(self, voter_id: str, candidate_name: str) -> List[str]:
        voter = self.voters[voter_id]
        cand_id = self.candidate_ids[candidate_name]
        params = self.cvk.get_public_params()
        n, e = params["n"], params["e"]

        self.log(f"--- Tamper Scenario for {voter_id} ---")

        # Prepare and get signatures
        blinded_parts = voter.prepare_vote(cand_id, n, e)
        signed_blinded = self.cvk.sign_blind_parts(voter_id, blinded_parts)
        unblinded_sigs = list(voter.unblind_signatures(signed_blinded, n))

        # Tamper with Part 1 content
        tampered_part = (voter.parts[0] + 1) % n
        self.log("Attacker: Tampering with part contents...")

        res1 = self.lcs[0].process_partial(
            voter.anonymous_id, tampered_part, unblinded_sigs[0], params
        )
        if not res1:
            self.log(
                t(T.LAB6_LCS_PARTS_REJECTED, self.lang, anon_id=voter.anonymous_id[:8])
            )

        # Tamper with Signature
        self.log("Attacker: Tampering with signature...")
        tampered_sig = (unblinded_sigs[1] + 1) % n
        res2 = self.lcs[1].process_partial(
            voter.anonymous_id, voter.parts[1], tampered_sig, params
        )
        if not res2:
            self.log(
                t(T.LAB6_LCS_PARTS_REJECTED, self.lang, anon_id=voter.anonymous_id[:8])
            )
        else:
            self.log("ERROR: LC2 accepted tampered signature!")

        return self.logs
