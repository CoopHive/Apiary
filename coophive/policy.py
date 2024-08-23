class Policy:

    def __init__(self, type):
        self.type = type

    def make_decision(self, match, localInformation):
        # return "accept", "reject", or "negotiate" after accounting for the match, the local information, and the global information
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
