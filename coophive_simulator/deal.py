from coophive_simulator.data_attribute import DataAttribute
from coophive_simulator.deal_attributes_dict import deal_attributes


class Deal(DataAttribute):
    def __init__(self):
        super().__init__()
        self.data_attributes = deal_attributes
