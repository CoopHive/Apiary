from resource_offer_attributes_dict import resource_offer_attributes


class ResourceOffer:
    def __init__(self):
        self.data = {}

    def add_data(self, data_field: str, data_value: str):
        # enforces constraints on resource offers to enable matches
        if data_field not in resource_offer_attributes:
            raise Exception(f"trying to add invalid data field {data_field} to resource offer")
        else:
            self.data[data_field] = data_value

    def get_resource_offer_data(self):
        return self.data
