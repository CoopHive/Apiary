from deal_attributes_dict import deal_attributes


class Deal:
    def __init__(self):
        self.data = {}

    def add_data(self, data_field: str, data_value: str):
        # enforces constraints on deals to enable matches
        if data_field not in deal_attributes:
            raise Exception(f"trying to add invalid data field {data_field}")
        else:
            self.data[data_field] = data_value

