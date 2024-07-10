# TODO: make machine CIDs unique
from coophive_simulator.data_attribute import DataAttribute
from coophive_simulator.machine_attributes_dict import machine_attributes


class Machine(DataAttribute):
    static_uuid = 0

    def __init__(self):
        super().__init__()
        self.data_attributes = machine_attributes
        # set machine uuid
        self.uuid = Machine.static_uuid
        # increment universal uuid counter
        Machine.static_uuid += 1

    def get_machine_uuid(self):
        return self.uuid
