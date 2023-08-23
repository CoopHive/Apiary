from utils import *
from machine import Machine
from service_provider import ServiceProvider
from solver import Solver
from match import Match
from smart_contract import SmartContract



class ResourceProvider(ServiceProvider):
    def __init__(self, public_key: str):
        # machines maps CIDs -> machine metadata
        super().__init__(public_key)
        self.machines = {}
        self.solver_url = None
        self.solver = None
        self.smart_contract = None

    def get_solver(self):
        return self.solver

    def connect_to_solver(self, url: str, solver: Solver):
        self.solver_url = url
        self.solver = solver
        solver.subscribe_event(self.handle_solver_event)

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)

    def add_machine(self, machine_id: CID, machine: Machine):
        self.machines[machine_id.hash] = machine

    def remove_machine(self, machine_id):
        self.machines.pop(machine_id)

    def get_machines(self):
        return self.machines

    def create_resource_offer(self):
        pass

    def handle_solver_event(self, event):
        print(f"I, the RP have solver event {event.get_name(), event.get_data().get_id()}")
        # print(event.get_data().get_data()['resource_provider_address'], self.get_public_key())
        if event.get_name() == 'match':
            match = event.get_data()
            if match.get_data()['resource_provider_address'] == self.get_public_key():
                tx = Tx(sender=self.get_public_key(), value=1)
                self.smart_contract.agree_to_match(match, tx)

    def handle_smart_contract_event(self, event):
        print(f"I, the RP have smart contract event {event.get_name(), event.get_data().get_id()}")
