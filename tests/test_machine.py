import pytest

from coophive_simulator.machine import Machine


@pytest.fixture(autouse=True)
def reset_static_uuid():
    # Reset the static_uuid counter before each test
    Machine.static_uuid = 0


def test_unique_uuid():
    machine1 = Machine()
    machine2 = Machine()
    machine3 = Machine()

    assert machine1.get_machine_uuid() == 0
    assert machine2.get_machine_uuid() == 1
    assert machine3.get_machine_uuid() == 2


def test_unique_uuid_with_more_machines():
    machines = [Machine() for _ in range(100)]
    uuids = [machine.get_machine_uuid() for machine in machines]

    # Check if all UUIDs are unique
    assert len(uuids) == len(set(uuids))
    # Check if the UUIDs are in sequential order
    assert uuids == list(range(100))
