from utils import CID
from machine import Machine
from service_provider import ServiceProvider
from solver import Solver


class ResourceProvider(ServiceProvider):
    def __init__(self, public_key: str):
        # machines maps CIDs -> machine metadata
        super().__init__(public_key)
        self.machines = {}
        self.solver_url = None
        self.solver = None

    def get_solver(self):
        return self.solver

    def connect_to_solver(self, url: str, solver: Solver):
        self.solver_url = url
        self.solver = solver
        solver.subscribe_event(self.handle_event)

    def add_machine(self, machine_id: CID, machine: Machine):
        self.machines[machine_id.hash] = machine

    def remove_machine(self, machine_id):
        self.machines.pop(machine_id)

    def get_machines(self):
        return self.machines

    def create_resource_offer(self):
        pass

    def handle_event(self, event):
        print(f"I, the RP have event {event.get_name(), event.get_data().get_id()}")
