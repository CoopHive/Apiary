from service_provider_local_information import LocalInformation


class ServiceProvider:
    def __init__(self, address: str = None, url: str = None):
        self.address = address
        self.url = url
        self.local_information = LocalInformation()

    def get_address(self):
        return self.address

    def get_url(self):
        return self.url

    def get_local_information(self):
        return self.local_information