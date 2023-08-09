from contract import CID
from machine import Machine
from service_provider_local_information import LocalInformation

class ResourcePovider:
    def __init__(self, address: str):
        # machines maps CIDs -> machine metadata
        self.address = address
        self.machines = {}
        self.local_information = LocalInformation()

    def add_machine(self, machine_id: CID, machine: Machine):
        self.machines[machine_id.hash] = machine

    def remove_machine(self, machine_id):
        self.machines.pop(machine_id)

    def get_machines(self):
        return self.machines
