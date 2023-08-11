from resource_offer_attributes_dict import resource_offer_attributes
from hash_dict import hash_dict


class ResourceOffer:
    def __init__(self):
        self.data = {}
        self.id = None

    def add_data(self, data_field: str, data_value: str):
        # enforces constraints on resource offers to enable matches
        if data_field not in resource_offer_attributes:
            raise Exception(f"trying to add invalid data field {data_field}")
        else:
            self.data[data_field] = data_value

    def get_resource_offer_data(self):
        return self.data

    def set_id(self):
        self.id = hash_dict(self.data)

    def get_id(self):
        return self.id


