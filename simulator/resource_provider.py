from contract import CID
from machine import Machine

class ResourcePovider:
    def __init__(self):
        # machines maps CIDs -> machine metadata
        self.machines = {}

    def add_machine(self, machine_id: CID, machine: Machine):
        self.machines[machine_id.hash] = machine

    def remove_machine(self, machine_id):
        self.machines.pop(machine_id)

    def get_machines(self):
        return self.machines
