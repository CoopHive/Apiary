from contract import CID
from service_provider_local_information import LocalInformation
from collections import deque
from job import Job


class Client:
    def __init__(self, address):
        self.address = address
        # TODO: should determine the best data structure for this
        self.current_jobs = deque()
        self.local_information = LocalInformation()

    def add_job(self, job: Job):
        self.current_jobs.append(job)

    def get_jobs(self):
        return self.current_jobs

