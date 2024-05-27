from data_attribute import DataAttribute
from results_attributes_dict import result_attributes


class Result(DataAttribute):
    def __init__(self):
        super().__init__()
        self.data_attributes = result_attributes
        
    def get_data(self):
        data = {}
        for attribute in self.data_attributes:
            data[attribute] = getattr(self, attribute, None)
        return data
    
    def set_attributes(self, attributes):
        for key, value in attributes.items():
            if hasattr(self, key) or key in self.data_attributes:
                setattr(self, key, value)
