# TODO: make machine CIDs unique

class Machine:
    def __init__(self, machine_attributes: set):
        self.machine_attributes = machine_attributes
        self.data = {}

    def add_data(self, data_field: str, data_value: str):
        # enforces constraints on machine data to enable matches
        if data_field not in self.machine_attributes:
            raise Exception(f"trying to add invalid data field {data_field} to machine")
        else:
            self.data[data_field] = data_value

    def get_machine_data(self):
        return self.data
