from data_attribute import DataAttribute
from match_attributes_dict import match_attributes


class Match(DataAttribute):
    def __init__(self):
        super().__init__()
        self.data_attributes = match_attributes
