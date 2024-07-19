"""This module defines the Job class which is used to manage job requirements."""


class Job:
    """A class to represent a job with its requirements."""

    def __init__(self):
        """Initialize the Job."""
        self.requirements = None

    def get_job_requirements(self):
        """Retrieve the requirements for the job."""
        return self.requirements
