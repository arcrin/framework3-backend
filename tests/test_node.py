from node.base_node import BaseNode
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


class TestNode(unittest.TestCase):

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

  def test_set_cleared(self):
    node1 = ConcreteNode("Node 1")
    self.assertFalse(node1.is_cleared())

    node1.set_cleared()
    self.assertTrue(node1.is_cleared())

  def test_ready_to_process(self):
    node1 = ConcreteNode("Node 1")
    self.assertTrue(node1.ready_to_process())

    node2 = ConcreteNode("Node 2")
    node1.add_dependency(node2)
    self.assertFalse(node1.ready_to_process())

    node2.set_cleared()
    self.assertTrue(node1.ready_to_process())

  def test_node_state_change(self):
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

    node2.set_cleared()
    self.assertTrue(node1.ready_to_process())

    node1.set_cleared()
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


if __name__ == "__main__":
  unittest.main()