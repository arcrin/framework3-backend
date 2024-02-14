from node.base_node import BaseNode, NodeState
from unittest.mock import AsyncMock, Mock
import unittest

class ConcreteNode(BaseNode):
  def __init__(self, name: str="Node") -> None:
    super().__init__(name)
    self._result = None
    
  async def execute(self):
    self._result = True

  @property
  def result(self):
    return self._result
  
class NodeMissingProperty(BaseNode):
  async def execute(self): 
    pass


class TestNode(unittest.IsolatedAsyncioTestCase):

  def test_create_node(self):
    node = ConcreteNode("Script 1")
    self.assertEqual(node.name, "Script 1")

  def test_create_node_without_name(self):
    node = ConcreteNode()
    self.assertEqual(node.name, "Node")

  def test_node_has_no_dependencies(self):
    node = ConcreteNode("Node 1")
    self.assertEqual(node.dependencies, [])

  def test_node_has_empty_dependencies(self):
    node = ConcreteNode("Node 1")
    self.assertEqual(node.dependencies, [])

  def test_add_dependency(self):
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")
    node1.add_dependency(node2)
    self.assertIn(node2, node1.dependencies)

  def test_remove_dependency(self):
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")
    node1.add_dependency(node2)
    node1.remove_dependency(node2)
    self.assertNotIn(node2, node1.dependencies)

  async def test_set_cleared(self):
    node1 = ConcreteNode("Node 1")
    self.assertFalse(node1.is_cleared())

    await node1.set_cleared()
    self.assertTrue(node1.is_cleared())

  async def test_ready_to_process(self):
    node1 = ConcreteNode("Node 1")
    self.assertTrue(node1.ready_to_process())

    node2 = ConcreteNode("Node 2")
    node1.add_dependency(node2)
    self.assertFalse(node1.ready_to_process())

    await node2.set_cleared()
    self.assertTrue(node1.ready_to_process())

  async def test_node_state_change(self):
    # Create a ConcreteNode
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")

    self.assertFalse(node1.is_cleared())
    self.assertFalse(node2.is_cleared())
    self.assertTrue(node1.ready_to_process())
    self.assertTrue(node2.ready_to_process())
    self.assertFalse(node1.is_cleared())
    self.assertFalse(node2.is_cleared())
    
    node1.add_dependency(node2)
    self.assertFalse(node1.ready_to_process())

    await node2.set_cleared()
    self.assertTrue(node1.ready_to_process())

    await node1.set_cleared()
    self.assertTrue(node1.is_cleared())

    node3 = ConcreteNode("Node 3")
    node1.add_dependency(node3)

    self.assertFalse(node1.ready_to_process())
    self.assertFalse(node1.is_cleared())
    

  async def test_execute_result(self):
    node1 = ConcreteNode("Node 1")
    self.assertIsNone(node1.result)

    await node1.execute()
    self.assertTrue(node1.result)

  def test_dependents(self):
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")
    node3 = ConcreteNode("Node 3")

    self.assertEqual(node1.dependents, [])

    node1.add_dependency(node2)
    node1.add_dependency(node3)

    self.assertEqual(node2.dependents, [node1])
    self.assertEqual(node3.dependents, [node1])

    node1.remove_dependency(node2)

    self.assertEqual(node2.dependents, [])

  def test_set_on_ready_callback(self):
    node = ConcreteNode("Node 1")

    mock_callback = Mock()

    node.set_on_ready_callback(mock_callback)

    node.on_ready_callback(node)

    mock_callback.assert_called_once_with(node)

  async def test_notify_dependencies_resolved(self):
    node1 = ConcreteNode("Node 1")
    node2 = ConcreteNode("Node 2")
    node3 = ConcreteNode("Node 3")

    node1.add_dependency(node2)
    node1.add_dependency(node3) # on_ready_callback should be called here, after node3 is cleared

    mock_callback = AsyncMock()

    node1.set_on_ready_callback(mock_callback)

    self.assertEqual(node1.state, NodeState.NOT_PROCESSED)

    await node2.set_cleared()
    await node3.set_cleared()

    self.assertEqual(node1.state, NodeState.READY_TO_PROCESS)

    mock_callback.assert_called_once_with(node1)


if __name__ == "__main__":
  unittest.main()