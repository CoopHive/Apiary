from utils import *
from machine import Machine
from service_provider import ServiceProvider
from solver import Solver
from match import Match
from smart_contract import SmartContract
from result import Result
import docker
import time
from datetime import datetime
import logging
# JSON Logging
from log_json import log_json
import os


class ResourceProvider(ServiceProvider):
    def __init__(self, public_key: str):
        # machines maps CIDs -> machine metadata
        super().__init__(public_key)
        self.logger = logging.getLogger(f"Resource Provider {self.public_key}")
        logging.basicConfig(filename=f'{os.getcwd()}/local_logs', filemode='w', level=logging.DEBUG)
        self.machines = {}
        self.solver_url = None
        self.solver = None
        self.smart_contract = None
        self.current_deals = {}  # maps deal id to deals
        # changed to simulate running a docker job
        self.current_jobs = {}
        self.docker_client = docker.from_env()
        #self.current_job_running_times = {}  # maps deal id to how long the resource provider has been running the job
        self.deals_finished_in_current_step = []
        self.current_matched_offers = []

        self.docker_username = 'your_dockerhub_username'
        self.docker_password = 'your_dockerhub_password'

        self.login_to_docker()
        
        # added for negotiation API
        # HOW DO WE INTIALIZE THESE?! Maybe each job offer should have its own T_accept, T_reject instead of one overarching one for the client
        # maybe T_accept should be calculate_utility times 1.05
        self.T_accept = 15
        # maybe T_reject should be calculate_utility times 2.1
        self.T_reject = 30
    
    def login_to_docker(self):
        try:
            self.docker_client.login(username=self.docker_username, password=self.docker_password)
            #self.logger.info("Logged into Docker Hub successfully")
            log_json(self.logger, "Logged into Docker Hub successfully")
        except docker.errors.APIError as e:
            #self.logger.error(f"Failed to log into Docker Hub: {e}")
            log_json(self.logger, f"Failed to log into Docker Hub: {e}")

    def get_solver(self):
        return self.solver

    def get_smart_contract(self):
        return self.smart_contract

    def connect_to_solver(self, url: str, solver: Solver):
        self.solver_url = url
        self.solver = solver
        self.solver.subscribe_event(self.handle_solver_event)
        self.solver.get_local_information().add_resource_provider(self)
        # JSON logging
        log_json(self.logger, "Connected to solver", {"solver_url": url})

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)
        # JSON logging
        log_json(self.logger, "Connected to smart contract")

    def add_machine(self, machine_id: CID, machine: Machine):
        self.machines[machine_id.hash] = machine

    def remove_machine(self, machine_id):
        self.machines.pop(machine_id)

    def get_machines(self):
        return self.machines

    def create_resource_offer(self):
        pass

    def _agree_to_match(self, match: Match):
        timeout_deposit = match.get_data()['timeout_deposit']
        tx = self._create_transaction(timeout_deposit)
        #tx = Tx(sender=self.get_public_key(), value=timeout_deposit)
        self.get_smart_contract().agree_to_match(match, tx)
        # JSON logging
        log_json(self.logger, "Agreed to match", {"match_id": match.get_id()})


    def handle_solver_event(self, event):
        # JSON logging
        event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
        log_json(self.logger, "Received solver event", {"event_data": event_data})

        #self.logger.info(f"have solver event {event.get_name(), event.get_data().get_id()}")
        if event.get_name() == 'match':
            match = event.get_data()
            if match.get_data()['resource_provider_address'] == self.get_public_key():
                self.current_matched_offers.append(match)

    # TODO: Implement this function 
    def handle_p2p_event(self, event):
        # if the resource provider hears about a job_offer, it should check if its an appropriate match the way handle_solver_event
        # determines that a match exists (if all required machine keys (CPU, RAM) have exactly the same values in both the job offer 
        # and the resource offer) -> then create a match and append to current_matched_offers.
        pass

    def handle_smart_contract_event(self, event):
        if event.get_name() == 'mediation_random':
            #JSON logging
            event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
            log_json(self.logger, "Received smart contract event", {"event_data": event_data})
            #self.logger.info(f"have smart contract event {event.get_name()}")        
        elif event.get_name() == 'deal':
            #JSON logging
            event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
            log_json(self.logger, "Received smart contract event", {"event_data": event_data})
            #self.logger.info(f"have smart contract event {event.get_name(), event.get_data().get_id()}")
            deal = event.get_data()
            deal_data = deal.get_data()
            deal_id = deal.get_id()
            if deal_data['resource_provider_address'] == self.get_public_key():
                self.current_deals[deal_id] = deal
                # changed to simulate running a docker job
                container = self.docker_client.containers.run("alpine", "sleep 30", detach=True)
                self.current_jobs[deal_id] = container
                #self.current_job_running_times[deal_id] = 0

    def post_result(self, result: Result, tx: Tx):
        self.get_smart_contract().post_result(result, tx)
        log_json(self.logger, "Posted result", {"result_id": result.get_id()})

    def create_result(self, deal_id):
        # JSON logging
        result_log_data = {"deal_id": deal_id}
        log_json(self.logger, "Creating result", result_log_data)
        #self.logger.info(f"posting the result for deal {deal_id}")
        result = Result()
        result.add_data('deal_id', deal_id)
        instruction_count = 1
        result.add_data('instruction_count', instruction_count)
        result.set_id()
        result.add_data('result_id', result.get_id())
        cheating_collateral_multiplier = self.current_deals[deal_id].get_data()['cheating_collateral_multiplier']
        cheating_collateral = cheating_collateral_multiplier * int(instruction_count)
        tx = self._create_transaction(cheating_collateral)
        #tx = Tx(sender=self.get_public_key(), value=cheating_collateral)
        return result, tx

    def update_finished_deals(self):
        # remove finished deals from list of current deals and running jobs
        for deal_id in self.deals_finished_in_current_step:
            del self.current_deals[deal_id]
            # changed to simulate running a docker job
            del self.current_jobs[deal_id]
        # clear list of deals finished in current step
        self.deals_finished_in_current_step.clear()

    def handle_completed_job(self, deal_id):
        # added to simulate running a docker job
        container = self.current_jobs[deal_id]
        container.stop()
        container.remove()
        result, tx = self.create_result(deal_id)
        self.post_result(result, tx)
        self.deals_finished_in_current_step.append(deal_id)

    def update_job_running_times(self):
        # changed to simulate running a docker job
        for deal_id, container in self.current_jobs.items():
            container.reload()
            if container.status == "exited":
                self.handle_completed_job(deal_id)
        self.update_finished_deals()

    def make_match_decision(self, match, algorithm):
        #print("entered make_match_decision")
        if algorithm == 'accept_all':
            self._agree_to_match(match)
        elif algorithm == 'accept_reject':
            #print("entered accept_reject")
            #   Calculate the utility of this match
            #   Find the best match for this resource offer  
            #   Accept if this match has the highest utility of all matches and if the utility is acceptable (above a certain threshold T_accept).
            #   Reject if this match does not have the highest utility of all matches OR it has the highest utility of all matches but the
            #   utility is not acceptable (below a certain threshold T_accept).
            match_utility = self.calculate_utility(match)
            best_match = self.find_best_match_for_resource_offer(match.get_data()['resource_offer'])
            # could also check that match_utility > self.T_reject to make it more flexible (basically accept a match if its utility is over T_reject instead of over T_accept)
            if best_match == match and match_utility > self.T_accept:
                self._agree_to_match(match)
            else:
                self.reject_match(match)
        elif algorithm == 'accept_reject_negotiate':
            #   Find the best match for this resource offer. If this match is the best, calculate its utility. 
            #   Accept if this match if the utility is acceptable (above a certain threshold T_accept).
            #   Reject if this match does not have the highest utility of all matches OR it has the highest utility of all matches but the
            #   utility is not acceptable (below a certain threshold T_accept).
            #   Negotiate if the utility is within range of being acceptable (between T_reject and T_accept). Call some function negotiate_match
            #   that takes the match as an input and creates a similar but new match where the utility of the new match is > T_accept. 
            #                   Should be able to handle multiple negotiation rounds. 
            #                   IMPLEMENT NEGOTIATIONS OVER HTTP: Parameter for how many rounds until negotiation ends (ex: 5).
            best_match = self.find_best_match_for_resource_offer(match.get_data()['resource_offer'])
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
        #   Check whether there is already a deal in progress for the current resource offer, if yes, reject this match.
        #   Introduce a flexibility factor that allows flexibility for when a cient decides to negotiate or reject (manipulates T_reject or utility somehow).
        #       - It allows for some degree of negotiation, making the client less rigid and more adaptable to market conditions.
        #   T_accept and T_reject may be static or dynamically adjusted based on historical data or current market conditions.
    
    def is_only_match(self, match):
        resource_offer_id = match.get_data()['resource_offer']
        print("resource_offer_id is ", resource_offer_id)
        print("number of current matched offers is ", len(self.current_matched_offers))
        for m in self.current_matched_offers:
            #print("the resource_offer_id of this match is: ", m.get_data()['resource_offer'])
            if m != match and m.get_data()['resource_offer'] == resource_offer_id:
                #print("there is another match for this resource offer")
                return False
        return True

    # Currently, if two or more matches have the same utility, the best_match is the first one in current_matched_offers
    def find_best_match_for_resource_offer(self, resource_offer_id):
        best_match = None
        highest_utility = -float('inf')
        for match in self.current_matched_offers:
            if match.get_data()['resource_offer'] == resource_offer_id:
                utility = self.calculate_utility(match)
                if utility > highest_utility:
                    highest_utility = utility
                    best_match = match
        return best_match
    
    def calculate_revenue(self, match):
        data = match.get_data()
        price_per_instruction = data.get('price_per_instruction', 0)
        expected_number_of_instructions = data.get('expected_number_of_instructions', 0)
        return price_per_instruction * expected_number_of_instructions
    
    def calculate_time(self, match):
        data = match.get_data()
        time = data.get('timeout', 0)
        return time

    # Currently T_accept is -15 and T_reject to -30 but that DEFINITELY needs to be changed 
    # NOTE: this utility calculation is DIFFERENT for a resource provider than for a client
    def calculate_utility(self, match):
        """
        Calculate the utility of a match based on several factors.
        COST and TIME are the main determiners.
        """
        #abstract logic into calculate benefit and calculate cost, add necessary attributes to match or job offer or resource offer
        # calculate cost should be number of instructions * price per instruction
        expected_revenue = self.calculate_revenue(match)
        # calculate time should be timeout
        expected_time = self.calculate_time(match)
        # the resource provider wants to maximize revenue while minimizing time required to complete a job
        utility = expected_revenue - expected_time
        
        return utility

    
    # Implement rejection logic. If a client or compute node rejects a match, it needs to be offered that match again 
    # (either via the solver or p2p negotiation) in order to accept it.
    def reject_match(self, match):
        log_json(self.logger, "Rejected match", {"match_id": match.get_id()})
        pass

    # TODO: Implement negotiation logic. Implement HTTP communication for negotiation
    def negotiate_match(self, match):
        log_json(self.logger, "Negotiating match", {"match_id": match.get_id()})
        pass


    def resource_provider_loop(self):
        for match in self.current_matched_offers:
            #self._agree_to_match(match)
            self.make_match_decision(match, algorithm='accept_reject_negotiate')
        self.update_job_running_times()
        self.current_matched_offers.clear()


# todo when handling events, add to list to be managed later, i.e. don't start signing stuff immediately













