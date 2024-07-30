"""This module sets up and manages the main functionality of the coophive simulator.

It includes defining and handling the Address class, setting up various components such as solvers, machines, resource providers, clients,
resource offers, and job offers, and running the main simulation.
"""

import logging

from coophive.client import Client
from coophive.job import Job
from coophive.job_offer import JobOffer
from coophive.machine import Machine
from coophive.resource_offer import ResourceOffer
from coophive.resource_provider import ResourceProvider
from coophive.solver import Solver
from coophive.utils import CID, ServiceType


def main():
    """The main function to run the coophive simulator.

    This function sets up the solvers, machines, resource providers, clients, resource offers, and job offers.
    It adds data to these components, establishes relationships between them, and performs the solve operation.
    """
    # create solver
    new_solver_1_public_key = "11"
    new_solver_1_url = "http://solver.com"
    new_solver_1 = Solver(new_solver_1_public_key, new_solver_1_url)

    new_machine_1 = Machine()
    new_machine_1.add_data("CPU", "4")
    new_machine_1.add_data("RAM", "2")
    # should throw exception if GPU is not one of the machine attributes
    # new_machine_1.add_data('GPU', '3090')
    machine_data = new_machine_1.get_data()
    logging.info(machine_data)

    new_machine_2 = Machine()
    new_machine_2.add_data("CPU", "8")
    new_machine_2.add_data("RAM", "4")

    new_resource_provider_1_public_key = "new_resource_provider_1_public_key"
    new_resource_provider_1 = ResourceProvider(new_resource_provider_1_public_key)
    new_machine_1_CID = CID("new_machine_1_CID", {})
    new_machine_2_CID = CID("new_machine_2_CID", {})
    new_resource_provider_1.add_machine(new_machine_1_CID, new_machine_1)
    new_resource_provider_1.add_machine(new_machine_2_CID, new_machine_2)
    resource_provider_machines = new_resource_provider_1.get_machines()
    logging.info(resource_provider_machines)
    # should match above
    logging.info(resource_provider_machines[new_machine_1_CID.hash].get_data())
    logging.info(resource_provider_machines[new_machine_2_CID.hash].get_data())

    logging.info(resource_provider_machines[new_machine_1_CID.hash].get_machine_uuid())
    logging.info(resource_provider_machines[new_machine_2_CID.hash].get_machine_uuid())

    new_client_1_public_key = "new_client_1_public_key"
    new_client_1 = Client(new_client_1_public_key)
    new_job = Job()
    new_client_1.add_job(new_job)
    # print job requirements
    logging.info(list(new_client_1.get_jobs())[0].get_job_requirements())

    # add client and resource provider to each other's local information
    new_solver_1.local_information.add_service_provider(
        ServiceType.RESOURCE_PROVIDER,
        new_resource_provider_1_public_key,
        new_resource_provider_1,
    )
    # should print public key of first resource provider
    logging.info(
        list(
            new_solver_1.local_information.get_list_of_service_providers(
                ServiceType.RESOURCE_PROVIDER
            ).values()
        )[0].get_public_key()
    )

    new_solver_1.local_information.add_service_provider(
        ServiceType.CLIENT, new_client_1_public_key, new_client_1
    )
    # should print public key of first client
    logging.info(
        list(
            new_solver_1.local_information.get_list_of_service_providers(
                ServiceType.CLIENT
            ).values()
        )[0].get_public_key()
    )

    new_resource_offer_1 = ResourceOffer()
    new_resource_offer_1.add_data("CPU", "6")
    new_resource_offer_1.add_data("RAM", "3")
    new_resource_offer_1.add_data("owner", new_resource_provider_1_public_key)
    new_resource_offer_1.set_id()
    new_resource_offer_1_id = new_resource_offer_1.get_id()
    logging.info(new_resource_offer_1.get_id())

    new_job_offer_1 = JobOffer()
    new_job_offer_1.add_data("CPU", "6")
    new_job_offer_1.add_data("RAM", "3")
    new_job_offer_1.add_data("owner", new_client_1_public_key)
    new_job_offer_1.set_id()
    new_job_offer_1_id = new_job_offer_1.get_id()
    logging.info(new_job_offer_1.get_id())

    new_solver_1.local_information.add_resource_offer(
        new_resource_offer_1_id, new_resource_offer_1
    )
    new_solver_1.local_information.add_job_offer(new_job_offer_1_id, new_job_offer_1)

    logging.info(
        new_solver_1.local_information.get_resource_offers()[new_resource_offer_1_id]
        .get_data()
        .items()
    )
    logging.info(
        new_solver_1.local_information.get_job_offers()[new_job_offer_1_id]
        .get_data()
        .items()
    )

    new_solver_1.solve()
    new_match_1 = new_solver_1.get_events()[0].get_data()
    logging.info(new_match_1.get_data())
    logging.info(new_match_1.get_id())


if __name__ == "__main__":
    main()
