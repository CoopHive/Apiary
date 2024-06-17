from utils import *
from service_provider import ServiceProvider
from service_provider_local_information import LocalInformation
from collections import deque
from job import Job
from solver import Solver
from match import Match
from smart_contract import SmartContract
from log_json import log_json
import logging
import os


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
        self.current_deals = {}  # maps deal id to deals
        self.deals_finished_in_current_step = []
        self.current_matched_offers = []
        

    def get_solver(self):
        return self.solver

    def get_smart_contract(self):
        return self.smart_contract

    def connect_to_solver(self, url: str, solver: Solver):
        self.solver_url = url
        self.solver = solver
        self.solver.subscribe_event(self.handle_solver_event)
        self.solver.get_local_information().add_client(self)
        log_json(self.logger, "Connected to solver", {"solver_url": url})

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)
        log_json(self.logger, "Connected to smart contract")

    def add_job(self, job: Job):
        self.current_jobs.append(job)

    def get_jobs(self):
        return self.current_jobs

    def _agree_to_match(self, match: Match):
        client_deposit = match.get_data()['client_deposit']
        tx = self._create_transaction(client_deposit)
        self.get_smart_contract().agree_to_match(match, tx)
        log_json(self.logger, "Agreed to match", {"match_id": match.get_id()})


    def handle_solver_event(self, event):
        event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
        log_json(self.logger, "Received solver event", {"event_data": event_data})
        if event.get_name() == 'match':
            match = event.get_data()
            if match.get_data()['client_address'] == self.get_public_key():
                self.current_matched_offers.append(match)
    
    # TODO: Implement this function 
    def handle_p2p_event(self, event):
        # if the client hears about a resource_offer, it should check if its an appropriate match the way handle_solver_event
        # determines that a match exists (if all required machine keys (CPU, RAM) have exactly the same values in both the job offer 
        # and the resource offer) -> then create a match and append to current_matched_offers.
        pass


    def decide_whether_or_not_to_mediate(self, event):
        # for now, always mediate
        return True
        
    def request_mediation(self, event):        
        log_json(self.logger, "Requesting mediation", {"event_name": event.get_name()})
        self.smart_contract.mediate_result(event)

    def pay_compute_node(self, event):
        result = event.get_data()
        result_data = result.get_data()
        deal_id = result_data['deal_id']
        if deal_id in self.current_deals.keys():
            result_instruction_count = result_data['instruction_count']
            result_instruction_count = float(result_instruction_count)
            price_per_instruction = self.current_deals[deal_id].get_data()['price_per_instruction']
            payment_value = result_instruction_count * price_per_instruction
            log_json(self.logger, "Paying compute node", {"deal_id": deal_id, "payment_value": payment_value})
            tx = Tx(sender=self.get_public_key(), value=payment_value)
            self.smart_contract.post_client_payment(result, tx)
            self.deals_finished_in_current_step.append(deal_id)
    
    def handle_smart_contract_event(self, event):
        if event.get_name() == 'mediation_random':
            event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
            log_json(self.logger, "Received smart contract event", {"event_data": event_data})
        if event.get_name() == 'deal':
            event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
            log_json(self.logger, "Received smart contract event", {"event_data": event_data})
            deal = event.get_data()
            deal_data = deal.get_data()
            deal_id = deal.get_id()
            if deal_data['client_address'] == self.get_public_key():
                self.current_deals[deal_id] = deal

        if event.get_name() == 'result':
            # decide whether to mediate result
            mediate_flag = self.decide_whether_or_not_to_mediate(event)
            if mediate_flag:
                mediation_result = self.request_mediation(event)
                """
                mediation should be handled automatically by the smart contract
                in fact, shouldn't the payment also be handled automatically by the smart contract?
                """
            # if not requesting mediation, send payment to compute node
            else:
                self.pay_compute_node(event)

    def update_finished_deals(self):
        # remove finished deals from list of current deals and running jobs
        for deal_id in self.deals_finished_in_current_step:
            del self.current_deals[deal_id]
        # clear list of deals finished in current step
        self.deals_finished_in_current_step.clear()

    def make_match_decision(self, match, algorithm):
        if algorithm == 'accept_all':
            self._agree_to_match(match)
        elif algorithm == 'accept_reject':
            match_utility = self.calculate_utility(match)
            best_match = self.find_best_match_for_job(match.get_data()['job_offer'])
            # could also check that match_utility > self.T_reject to make it more flexible (basically accept a match if its utility is over T_reject instead of over T_accept)
            # TODO: update where T_accept is accessed from if its moved to job_offer
            if best_match == match and match_utility > match.get_data()['T_accept']:
                self._agree_to_match(match)
            else:
                self.reject_match(match)
        elif algorithm == 'accept_reject_negotiate':
            #   Negotiate if the utility is within range of being acceptable (between T_reject and T_accept). Call some function negotiate_match
            #   that takes the match as an input and creates a similar but new match where the utility of the new match is > T_accept. 
            #                   Should be able to handle multiple negotiation rounds. 
            #                   IMPLEMENT NEGOTIATIONS OVER HTTP: Parameter for how many rounds until negotiation ends (ex: 5).
            best_match = self.find_best_match_for_job(match.get_data()['job_offer'])
            if best_match == match:
                utility = self.calculate_utility(match)
                # TODO: update where T_accept is accessed from if its moved to job_offer
                if utility > match.get_data()['T_accept']:
                    self._agree_to_match(match)
                # TODO: update where T_reject is accessed from if its moved to job_offer
                elif utility < match.get_data()['T_reject']:
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
        #   T_accept and T_reject may be static or dynamically adjusted based on historical data or current market conditions.

    def find_best_match_for_job(self, job_offer_id):
        best_match = None
        highest_utility = -float('inf')
        for match in self.current_matched_offers:
            if match.get_data()['job_offer'] == job_offer_id:
                utility = self.calculate_utility(match)
                if utility > highest_utility:
                    highest_utility = utility
                    best_match = match
        return best_match
    
    def calculate_cost(self, match):
        data = match.get_data()
        price_per_instruction = data.get('price_per_instruction', 0)
        expected_number_of_instructions = data.get('expected_number_of_instructions', 0)
        return price_per_instruction * expected_number_of_instructions
    
    def calculate_benefit(self, match):
        data = match.get_data()
        expected_benefit_to_client = data.get('expected_benefit_to_client', 0)
        return expected_benefit_to_client

    def calculate_utility(self, match):
        expected_cost = self.calculate_cost(match)
        expected_benefit = self.calculate_benefit(match)
        utility = expected_benefit - (expected_cost)
        return utility

    
    # Implement rejection logic. If a client or compute node rejects a match, it needs to be offered that match again 
    # (either via the solver or p2p negotiation) in order to accept it.
    def reject_match(self, match):
        log_json(self.logger, "Rejected match", {"match_id": match.get_id()})
        pass

    # TODO: Implement negotiation logic. Implement HTTP communication for negotiation
    def negotiate_match(self, match, max_rounds=5):
        log_json(self.logger, "Negotiating match", {"match_id": match.get_id()})
        for _ in range(max_rounds):
            new_match_offer = self.create_new_match_offer(match)
            response = self.communicate_request_to_party(match.get_data()['resource_provider_address'], new_match_offer)
            if response['accepted']:
                self._agree_to_match(response['match'])
                return
            match = response['counter_offer']
        self.reject_match(match)

    def create_new_match_offer(self, match):
        data = match.get_data()
        new_data = data.copy()
        new_data['price_per_instruction'] = data['price_per_instruction'] * 0.95  # For example, reduce the price
        new_match = Match(new_data)
        return new_match
    
    def communicate_request_to_party(self, party_id, match_offer):
        # Simulate communication - this would need to be implemented with actual P2P or HTTP communication
        response = self.simulate_communication(party_id, match_offer)
        return response
    
    def simulate_communication(self, party_id, match_offer):
        log_json(self.logger, "Simulating communication", {"party_id": party_id, "match_offer": match_offer.get_data()})
        # In a real implementation, this function would send a request to the party_id and wait for a response.
        response = {
            'accepted': False,
            'counter_offer': self.create_new_match_offer(match_offer)
        }
        # TODO: update where T_accept is accessed from if its moved to job_offer
        if self.calculate_utility(match_offer) > match_offer.get_data()['T_accept']:
            response['accepted'] = True
            response['match'] = match_offer
        return response

    def client_loop(self):
        for match in self.current_matched_offers:
            # use *args, **kwargs
            self.make_match_decision(match, algorithm='accept_reject_negotiate')
        self.update_finished_deals()
        self.current_matched_offers.clear()

