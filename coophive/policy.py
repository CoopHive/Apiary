"""This module defines the Policy class used when clients/resource_providers make decisions on a match within the CoopHive simulator.
"""
class Policy:
    """A policy in the coophive simulator that interacts with clients and resource providers to accept, reject, or negotiate a match."""
    def __init__(self, type):
        """Initialize a new Policy instance.

        Args:
            type (str): The type of policy.
        """
        self.type = type

    def make_decision(self, match, localInformation):
        """ Return "accept", "reject", or "negotiate" after accounting for the match, the local information, and the global information."""
        if self.type == "a":
            return "accept", None
        elif self.type == "b":
            return "reject", None
        elif self.type == "c":
            counteroffer = match
            return "negotiate", counteroffer

            # best_match = self.find_best_match(match.get_data()["job_offer"])
            # if best_match == match:
            #     utility = self.calculate_utility(match)
            #     if utility > match.get_data()["job_offer"]["T_accept"]:
            #         self._agree_to_match(match)
            #     elif utility < match.get_data()["job_offer"]["T_reject"]:
            #         self.reject_match(match)
            #     else:
            #         self.negotiate_match(match)
            # else:
            #     self.reject_match(match)
