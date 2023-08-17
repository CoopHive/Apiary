class Event:
    def __init__(self, name: str, data):
        self.name = name
        self.data = data

    def get_name(self):
        return self.name

    def get_data(self):
        return self.data
