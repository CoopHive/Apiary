# TODO: make machine CIDs unique
from machine_attributes_dict import machine_attributes


class Machine:
    static_uuid = 0

    def __init__(self):
        # set machine uuid
        self.uuid = Machine.static_uuid
        # increment universal uuid counter
        Machine.static_uuid += 1
        self.data = {}

    def add_data(self, data_field: str, data_value: str):
        # enforces constraints on machine data to enable matches
        if data_field not in machine_attributes:
            raise Exception(f"trying to add invalid data field {data_field} to machine")
        else:
            self.data[data_field] = data_value

    def get_machine_data(self):
        return self.data

    def get_machine_uuid(self):
        return self.uuid
