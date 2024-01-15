import unittest
from node.base_node import BaseNode

class TestNode(unittest.TestCase):
  def test_create_node(self):
    node = BaseNode("Script 1")
    self.assertEqual(node.name, "Script 1")

  def test_create_node_without_name(self):
    node = BaseNode()
    self.assertEqual(node.name, "Node")

  def test_node_has_no_dependencies(self):
    node = BaseNode("Node 1")
    self.assertEqual(node.dependencies, [])

  def test_node_has_empty_dependencies(self):
    node = BaseNode("Node 1")
    self.assertEqual(node.dependencies, [])

  def test_add_dependency(self):
    node1 = BaseNode("Node 1")
    node2 = BaseNode("Node 2")
    node1.add_dependency(node2)
    self.assertIn(node2, node1.dependencies)

  def test_remove_dependency(self):
    node1 = BaseNode("Node 1")
    node2 = BaseNode("Node 2")
    node1.add_dependency(node2)
    node1.remove_dependency(node2)
    self.assertNotIn(node2, node1.dependencies)

  

if __name__ == "__main__":
  unittest.main()