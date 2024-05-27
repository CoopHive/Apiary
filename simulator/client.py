from utils import *
from service_provider import ServiceProvider
from service_provider_local_information import LocalInformation
from collections import deque
from job import Job
from solver import Solver
from match import Match
from smart_contract import SmartContract
#JSON logging
from log_json import log_json
import logging
import os
from event import Event
from deal import Deal
from result import Result


class Client(ServiceProvider):
    def __init__(self, address: str):
        super().__init__(address)
        self.logger = logging.getLogger(f"Client {self.public_key}")
        logging.basicConfig(filename=f'{os.getcwd()}/local_logs', filemode='w', level=logging.DEBUG)
        # TODO: should determine the best data structure for this
        self.current_jobs = deque()
        self.local_information = LocalInformation()
        self.solver_url = None
        self.solver = None
        self.current_deals: dict[str, Deal] = {}  # maps deal id to deals
        self.deals_finished_in_current_step = []
        self.current_matched_offers: list[Match] = []
        # added for negotiation API
        # HOW DO WE INTIALIZE THESE?! Maybe each job offer should have its own T_accept, T_reject instead of one overarching one for the client
        # maybe T_accept should be calculate_utility times 1.05
        self.T_accept = -15
        # maybe T_reject should be calculate_utility times 2.1
        self.T_reject = -30

    def get_solver(self):
        return self.solver

    def get_smart_contract(self):
        return self.smart_contract

    def connect_to_solver(self, url: str, solver: Solver):
        self.solver_url = url
        self.solver = solver
        self.solver.subscribe_event(self.handle_solver_event)
        self.solver.get_local_information().add_client(self)
        #JSON logging
        log_json(self.logger, "Connected to solver", {"solver_url": url})

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)
        #JSON logging
        log_json(self.logger, "Connected to smart contract")

    def add_job(self, job: Job):
        self.current_jobs.append(job)

    def get_jobs(self):
        return list(self.current_jobs)

    def _agree_to_match(self, match: Match):
        client_deposit = match.get_data().get('client_deposit')
        tx = self._create_transaction(client_deposit)
        #tx = Tx(sender=self.get_public_key(), value=client_deposit)
        self.get_smart_contract().agree_to_match(match, tx)
        #JSON logging
        log_json(self.logger, "Agreed to match", {"match_id": match.get_id()})


    def handle_solver_event(self, event: Event):
        data = event.get_data()
        
        if not isinstance(data, Match):
            self.logger.warning(f"Unexpected data type received in solver event: {type(data)}")
            log_json(self.logger, "Received solver event with unexpected data type", {"name": event.get_name()})
            return

        # At this point, we know data is of type Match
        event_data = {"name": event.get_name(), "id": data.get_id()}
        log_json(self.logger, "Received solver event", {"event_data": event_data})
        
        if event.get_name() == 'match':
            match = data
            match_data = match.get_data()
            if isinstance(match_data, dict) and match_data.get('client_address') == self.get_public_key():
                self.current_matched_offers.append(match)


    def decide_whether_or_not_to_mediate(self, event: Event):
        # for now, always mediate
        return True
        
    def request_mediation(self, event: Event):        
        self.logger.info(f"requesting mediation {event.get_name()}")
        self.smart_contract.mediate_result(event)

    def pay_compute_node(self, event: Event):
        result = event.get_data()
        if not isinstance(result, Result):
            self.logger.warning(f"Unexpected data type received in solver event: {type(result)}")
        else:
            result_data = result.get_data()
            deal_id = result_data['deal_id']
            if deal_id in self.current_deals.keys():
                self.smart_contract.deals[deal_id] = self.current_deals.get(deal_id)
                result_instruction_count = result_data['instruction_count']
                result_instruction_count = float(result_instruction_count)
                price_per_instruction = self.current_deals.get("deal_123").get_data().get('price_per_instruction')
                payment_value = result_instruction_count * price_per_instruction
                tx = Tx(sender=self.get_public_key(), value=payment_value)
                
                self.smart_contract.post_client_payment(result, tx)
                
                
                self.deals_finished_in_current_step.append(deal_id)
        
    def handle_smart_contract_event(self, event: Event):
        data = event.get_data()

        if isinstance(data, Deal) or isinstance(data, Match):
            event_data = {"name": event.get_name(), "id": data.get_id()}
            log_json(self.logger, "Received smart contract event", {"event_data": event_data})
        else:
            log_json(self.logger, "Received smart contract event with unexpected data type", {"name": event.get_name()})
        
        if isinstance(data, Deal):
            deal = data
            deal_data = deal.get_data()
            deal_id = deal.get_id()
            if deal_data['client_address'] == self.get_public_key():
                self.current_deals[deal_id] = deal

        elif isinstance(data, Match):
            match = data
            # decide whether to mediate result
            if event.get_name() == 'result':
                mediate_flag = self.decide_whether_or_not_to_mediate(event)
                if mediate_flag:
                    self.request_mediation(event)
                else:
                    self.pay_compute_node(event)


    def update_finished_deals(self):
        # remove finished deals from list of current deals and running jobs
        for deal_id in self.deals_finished_in_current_step:
            del self.current_deals[deal_id]
        # clear list of deals finished in current step
        self.deals_finished_in_current_step.clear()

    def make_match_decision(self, match: Match, algorithm):
        #print("entered make_match_decision")
        if algorithm == 'accept_all':
            # This is a simple algorithm for testing but in practice, it is not wise for the client to simply accept all 
            # acceptable proposals from resource providers and select the best proposal from them because the client may be forced to 
            # pay a large amount of penalty fees for reneging on many deals
            self._agree_to_match(match)
        elif algorithm == 'accept_reject':
            #print("entered accept_reject")
            # If this is the only match for this job offer:
            #   Naive Implementation: Accept.  
            #   Complex Implementation: Accept if the utility is acceptable (above a certain threshold T_accept). Utility is some formula comprised of price per instruction, 
            #            client deposit, timeout, timeout deposit, cheating collateral multiplier, verification method, and mediators.
            #            Reject if the utility is not acceptable (below a certain threshold T_accept).  
            # If this is not the only match for this job offer:
            #   Calculate the utility of each match for this job offer.  
            #   Accept if this match has the highest utility and if the utility is acceptable (above a certain threshold T_accept).
            #   Reject if this match does not have the highest utility OR it has the highest utility but the utility is not acceptable (below a certain threshold T_accept).
            match_utility = self.calculate_utility(match)
            if self.is_only_match(match):
                #print("is the only match in accept_reject")    
                if match_utility > self.T_accept:
                    print("Agreeing to match because it is the only match and match's utility is ", match_utility, " which is greater than T_accept: ", self.T_accept)
                    self._agree_to_match(match)
                else:
                    print("Rejecting match because it is the only match and match's utility is ", match_utility, " which is less than T_accept: ", self.T_accept)
                    self.reject_match(match)
            else:
                print("is NOT the only match in accept_reject")
                best_match = self.find_best_match_for_job(match.get_data().get('job_offer'))
                if best_match == match and match_utility > self.T_accept:
                    self._agree_to_match(match)
                else:
                    self.reject_match(match)
        elif algorithm == 'accept_reject_negotiate':
            # If this is the only match for this job offer:
            #   Naive Implementation: Accept  
            #   Complex Implementation: Accept if the utility is acceptable (above a certain threshold T_accept). Utility is some formula comprised of price per instruction, 
            #            client deposit, timeout, timeout deposit, cheating collateral multiplier, verification method, and mediators. 
            #            Reject if the utility is not at all acceptable (below a certain threshold T_reject).
            #            Negotiate if the utility is within range of being acceptable (between T_reject and T_accept). Call some function negotiate_match 
            #                   that takes the match as an input and creates a similar but new match where the utility of the new match is > T_accept. 
            #                   Should be able to handle multiple negotiation rounds. 
            #                   IMPLEMENT NEGOTIATIONS OVER HTTP: Parameter for how many rounds until negotiation ends (ex: 5). 
            # If this is not the only match for this job offer:
            #   Calculate the utility of each match for this job offer. 
            #   Accept if this match has the highest utility and if the utility is acceptable (above a certain threshold T_accept).
            #       - Need tie breaking mechanism if tied for highest utility
            #   Reject this match does not have the highest utility.
            #   Negotiate if this match has the highest utility but the utility is not acceptable (below a certain threshold T_accept).
            if self.is_only_match(match):
                #print("accept_reject_negotiate and is only match")
                utility = self.calculate_utility(match)
                if utility > self.T_accept:
                    print("Agreeing to match because it is the only match and match's utility is ", utility, " which is greater than T_accept: ", self.T_accept)
                    self._agree_to_match(match)
                elif utility < self.T_reject:
                    print("Rejecting match because it is the only match and match's utility is ", utility, " which is less than T_reject: ", self.T_reject)
                    self.reject_match(match)
                else:
                    print("Negotiating match because it is the only match and match's utility is ", utility, " which is in between T_accept and T_reject.")
                    self.negotiate_match(match)
            else:
                print("accept_reject_negotiate and is NOT only match")
                best_match = self.find_best_match_for_job(match.get_data().get('job_offer'))
                if best_match == match:
                    utility = self.calculate_utility(match)
                    if utility > self.T_accept:
                        self._agree_to_match(match)
                    elif utility < self.T_reject:
                        self.reject_match(match)
                    else:
                        self.negotiate_match(match)
                else:
                    self.reject_match(match)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        # Other considerations: 
        #   Check whether there is already a deal in progress for the current job offer, if yes, reject this match.
        #   Introduce a flexibility factor that allows flexibility for when a cient decides to negotiate or reject (manipulates T_reject or utility somehow).
        #       - It allows for some degree of negotiation, making the client less rigid and more adaptable to market conditions.
        #   Utility function should be well-defined and customizable, allowing adjustments based on different client requirements.
        #   T_accept and T_reject may be static or dynamically adjusted based on historical data or current market conditions.
    
    def is_only_match(self, match: Match):
        job_offer_id = match.get_data().get('job_offer')
        print("job_offer_id is ", job_offer_id)
        print("number of current matched offers is ", len(self.current_matched_offers))
        for m in self.current_matched_offers:
            #print("the job_offer_id of this match is: ", m.get_data()['job_offer'])
            if m != match and m.get_data().get('job_offer') == job_offer_id:
                #print("there is another match for this job offer")
                return False
        return True

    def find_best_match_for_job(self, job_offer_id):
        best_match = None
        highest_utility = -float('inf')
        for match in self.current_matched_offers:
            if match.get_data().get('job_offer') == job_offer_id:
                utility = self.calculate_utility(match)
                if utility > highest_utility:
                    highest_utility = utility
                    best_match = match
        return best_match

    # More negative utility = worse for client, Closer to zero utility = better for client
    # Utility always negative in this calculation, so trying to have utility closest to zero
    # Thus set T_accept to -15 for some flexibility and T_reject to -30
    def calculate_utility(self, match: Match):
        """
        Calculate the utility of a match based on several factors.
        COST and TIME are the main determiners.
        
        Utility formula:
        - Lower price per instruction is better (weighted negatively).
        - Lower client deposit is better (weighted negatively, with less importance than price).
        - Shorter timeout is better (weighted negatively).
        - Lower timeout deposit is better (weighted negatively, with less importance than timeout).
        """
        data = match.get_data()
        price_per_instruction = data.get('price_per_instruction')
        print("price_per_instruction is ", price_per_instruction)
        client_deposit = data.get('client_deposit')
        print("client_deposit is ", client_deposit)
        timeout = data.get('timeout')
        print("timeout is ", timeout)
        timeout_deposit = data.get('timeout_deposit')
        print("timeout_deposit is ", timeout_deposit)
        
        # Calculate utility with appropriate weights
        utility = (
            price_per_instruction * -1 + 
            client_deposit * -0.5 + 
            timeout * -1 + 
            timeout_deposit * -0.3
        )
        
        return utility

    
    def reject_match(self, match):
    # Implement rejection logic
        log_json(self.logger, "Rejected match", {"match_id": match.get_id()})
        pass

    def negotiate_match(self, match):
        # Implement negotiation logic
        log_json(self.logger, "Negotiated match", {"match_id": match.get_id()})
        pass


    # for each match, call some function with an input comprised of the match and a match algorithm 
    # that decides whether the client should accept, reject, or negotiate the deal
    # i.e. self.make_match_decision(match, algorithm='accept_all') would call self._agree_to_match(match) 
    # i.e. self.make_match_decision(match, algorithm='accept_reject') would have the client only accept or reject the match, not allowing for negotiations
    # i.e. self.make_match_decision(match, algorithm='accept_reject_negotiate') would have the client accept, reject, or negotiate the match
    def client_loop(self):
        for match in self.current_matched_offers:
            # use *args, **kwargs
            self.make_match_decision(match, algorithm='accept_reject_negotiate')
            #self._agree_to_match(match)
        self.update_finished_deals()
        self.current_matched_offers.clear()

