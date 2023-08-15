from deal_attributes_dict import deal_attributes
from hash_dict import hash_dict


class Deal:
    def __init__(self):
        self.data = {}
        self.id = None

    def add_data(self, data_field: str, data_value: str):
        # enforces constraints on deals to enable matches
        if data_field not in deal_attributes:
            print(f"trying to add invalid data field {data_field}")
            raise Exception(f"trying to add invalid data field")
        else:
            self.data[data_field] = data_value

    def get_deal_data(self):
        return self.data

    def set_id(self):
        self.id = hash_dict(self.data)

    def get_id(self):
        return self.id
