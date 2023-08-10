# from contract import CID
from utils import CID
from service_provider import ServiceProvider
from service_provider_local_information import LocalInformation
from collections import deque
from job import Job


class Client(ServiceProvider):
    def __init__(self, address: str, url: str):
        super().__init__(address, url)
        # TODO: should determine the best data structure for this
        self.current_jobs = deque()
        self.local_information = LocalInformation()

    def add_job(self, job: Job):
        self.current_jobs.append(job)

    def get_jobs(self):
        return self.current_jobs

