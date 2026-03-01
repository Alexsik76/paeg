"""
Abstract base classes for the voting protocols.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseVoter(ABC):
    """
    Abstract Base Class for a Voter in the election protocol.
    """

    def __init__(self, voter_id: str, is_registered: bool = True):
        self.voter_id = voter_id
        self.is_registered = is_registered
        self.crypto_system = None  # Should be initialized in child classes

    @abstractmethod
    def vote(self, candidate_id: str, cvk_public_key: bytes) -> Any:
        """
        Process of casting a vote.
        Must return the ballot or payload sent to CVK.
        """
        pass


class BaseCVK(ABC):
    """
    Abstract Base Class for the Central Election Commission (CVK).
    """

    def __init__(self):
        self.logs: List[str] = []
        self.tallies: Dict[str, int] = {}
        self.registered_voters: set = set()
        self.has_voted: set = set()

    def log_action(self, action: str) -> None:
        """
        Log an action for the terminal output.
        """
        self.logs.append(action)

    def get_logs(self) -> List[str]:
        """
        Return the list of logs and clear them.
        """
        logs = self.logs.copy()
        self.logs.clear()
        return logs

    def register_voter(self, voter_id: str) -> None:
        """
        Register a voter.
        """
        self.registered_voters.add(voter_id)
        self.log_action(f"Registered voter with ID: {voter_id}")

    @abstractmethod
    def process_vote(self, payload: Any) -> bool:
        """
        Process an incoming vote payload.
        Returns True if the vote was valid, False otherwise.
        """
        pass
