class Policy():
    def __init__(self, name):
        self.name = name
    
    def calculate_result(match, localInformation):
        # return "accept", "reject", or "negotiate" after accounting for the match, the local information, and the global information
        best_match = self.find_best_match(match.get_data()["job_offer"])
        if best_match == match:
            utility = self.calculate_utility(match)
            if utility > match.get_data()["job_offer"]["T_accept"]:
                return "accept"
            elif utility < match.get_data()["job_offer"]["T_reject"]:
                return "reject"
            else:
                return "negotiate"
        else:
            return "reject"
