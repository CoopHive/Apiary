from utils import CID
from machine import Machine
from service_provider import ServiceProvider
from service_provider_local_information import LocalInformation

class ResourcePovider(ServiceProvider):
    def __init__(self, address: str, url: str):
        # machines maps CIDs -> machine metadata
        super().__init__(address, url)
        self.machines = {}
        self.local_information = LocalInformation()

    def add_machine(self, machine_id: CID, machine: Machine):
        self.machines[machine_id.hash] = machine

    def remove_machine(self, machine_id):
        self.machines.pop(machine_id)

    def get_machines(self):
        return self.machines

    def get_address(self):
        return self.address

    def get_url(self):
        return self.url
