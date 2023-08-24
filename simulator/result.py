from data_attribute import DataAttribute
from results_attributes_dict import result_attributes


class Result(DataAttribute):
    def __init__(self):
        super().__init__()
        self.data_attributes = result_attributes
