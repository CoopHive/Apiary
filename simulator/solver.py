from service_provider import ServiceProvider


class Solver(ServiceProvider):
    def __init__(self, address: str, url: str):
        super().__init__(address, url)
