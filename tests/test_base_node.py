# type: ignore
from _Node._BaseNode import BaseNode, NodeState
import pytest


class ConcreteNode(BaseNode):
    def __init__(self, name: str = "Node") -> None:
        super().__init__(name)
        self._result = None

    async def execute(self):
        self._result = True


class NodeMissingProperty(BaseNode):
    async def execute(self):
        pass


def test_create_node():
    node = ConcreteNode("Script 1")
    assert node.name == "Script 1"


def test_create_node_without_name():
    node = ConcreteNode()
    assert node.name == "Node"


def test_node_has_no_dependencies():
    node = ConcreteNode("Node 1")
    assert node.dependencies == []


def test_add_dependency():
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")
    node1.add_dependency(node2)
    assert node2 in node1.dependencies


def test_remove_dependency():
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")
    node1.add_dependency(node2)
    node1.remove_dependency(node2)
    assert node2 not in node1.dependencies


async def test_set_cleared():
    node1 = ConcreteNode("Node 1")
    assert not node1.is_cleared()

    await node1.set_cleared()
    assert node1.is_cleared()


async def test_ready_to_process():
    node1 = ConcreteNode("Node 1")
    assert node1.ready_to_process()

    node2 = ConcreteNode("Node 2")
    node1.add_dependency(node2)
    assert not node1.ready_to_process()

    await node2.set_cleared()
    assert node1.ready_to_process()


async def test_node_state_change():
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")

    assert not node1.is_cleared()
    assert not node2.is_cleared()
    assert node1.ready_to_process()
    assert node2.ready_to_process()
    assert not node1.is_cleared()
    assert not node2.is_cleared()

    node1.add_dependency(node2)
    assert not node1.ready_to_process()

    await node2.set_cleared()
    assert node1.ready_to_process()

    await node1.set_cleared()
    assert node1.is_cleared()

    node3 = ConcreteNode("Node 3")
    node1.add_dependency(node3)

    assert not node1.ready_to_process()
    assert not node1.is_cleared()


async def test_node_execute():
    node1 = ConcreteNode("Node 1")
    assert node1.result is None
    await node1.execute()
    assert node1.result


def test_dependents():
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")
    node3 = ConcreteNode("Node 3")

    assert node1.dependents == []

    node1.add_dependency(node2)
    node1.add_dependency(node3)

    assert node2.dependents == [node1]
    assert node3.dependents == [node1]

    node1.remove_dependency(node2)

    assert node2.dependents == []
    

async def test_notify_dependencies_resolved(mocker):
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")
    node3 = ConcreteNode("Node 3")

    node1.add_dependency(node2)
    node1.add_dependency(node3)

    mock_callback = mocker.AsyncMock()

    node1.set_scheduling_callback(mock_callback)

    assert node1.state == NodeState.NOT_PROCESSED

    await node2.set_cleared()
    assert mock_callback.call_count == 0

    await node3.set_cleared()
    assert mock_callback.call_count == 1

    assert node1.state == NodeState.READY_TO_PROCESS

    mock_callback.assert_called_once_with(node1)


def test_cyclic_dependency():
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")
    node3 = ConcreteNode("Node 3")

    node1.add_dependency(node2)
    node2.add_dependency(node3)

    with pytest.raises(ValueError):
        node3.add_dependency(node1)


async def test_reset(mocker):
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")
    node3 = ConcreteNode("Node 3")

    node3.add_dependency(node2)
    node2.add_dependency(node1)

    on_ready_callback = mocker.AsyncMock()
    node1.set_scheduling_callback(on_ready_callback)
    node2.set_scheduling_callback(on_ready_callback)
    node3.set_scheduling_callback(on_ready_callback)

    await node1.set_cleared()

    assert node1.state == NodeState.CLEARED

    assert on_ready_callback.call_count == 1 # node2 scheduled

    await node2.set_cleared()

    assert node2.state == NodeState.CLEARED

    assert on_ready_callback.call_count == 2 # node3 scheduled

    assert node3.ready_to_process()

    await node3.set_cleared()


    assert node3.state == NodeState.CLEARED 

    await node1.reset()

    assert node1.state == NodeState.READY_TO_PROCESS

    assert on_ready_callback.call_count == 3 # node1 scheduled

    # node2 and node3 are not ready to process, since node1 is not cleared yet
    assert node2.state == NodeState.NOT_PROCESSED
    assert node3.state == NodeState.NOT_PROCESSED

async def test_rest_dependents_labeled_as_cancelled():
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")

    node1.add_dependency(node2)

    node2._state = NodeState.CLEARED
    node1._state = NodeState.PROCESSING

    await node2.reset()
    
    # node2 should be ready for process because it doesn't have any dependency
    assert node2.state == NodeState.READY_TO_PROCESS
    assert node1.state == NodeState.CANCEL
    

def test_error_property():
    node = ConcreteNode("Node 1")
    value_error = ValueError("An error occurred")

    node.error = value_error
    with pytest.raises(ValueError):
        raise node.error   