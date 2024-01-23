from producer_consumer.dependency_checker import DependencyChecker
from node.base_node import BaseNode
from typing import List
import asyncio
import unittest

class ConcreteNode(BaseNode):
  async def execute(self):
    pass

  @property
  def result(self):
    return self._result

class TestDependencyChecker(unittest.IsolatedAsyncioTestCase):
  def setUp(self):
    self.node1 = ConcreteNode("node1")  
    self.node2 = ConcreteNode("node2")
    self.node3 = ConcreteNode("node3")

    self.node1.add_dependency(self.node2)
    self.node3.add_dependency(self.node1)

    self.node_list: List[BaseNode] = [self.node1, self.node2, self.node3]
    self.output_queue:asyncio.Queue[BaseNode] = asyncio.Queue()
    self.dependency_checker = DependencyChecker(self.node_list, self.output_queue)

  async def test_process_queue(self):

    self.assertFalse(self.node_list[0].is_cleared())
    self.assertFalse(self.node_list[1].is_cleared())
    self.assertFalse(self.node_list[2].is_cleared())

    # Clear the first two nodes
    self.node2.set_cleared()

    self.assertTrue(self.node2.is_cleared())
    self.assertTrue(self.node1.ready_to_process())
    self.assertFalse(self.node3.ready_to_process())

    # Run the process_queue method in a separate task because it's an infinite loop
    task = asyncio.create_task(self.dependency_checker.process_queue())

    # Give the task a moment to start and call _output_queue.put
    await asyncio.sleep(1)

    # Cancel the task to stop the infinite loop
    task.cancel()

    # Assert that the cleared nodes were put in the output queue
    self.assertTrue(self.node1 in list(self.output_queue._queue)) # type: ignore
    self.assertTrue(self.node2 in list(self.output_queue._queue)) # type: ignore

    # Assert that the uncleared node was not put in the output queue
    self.assertFalse(self.node3 in list(self.output_queue._queue)) # type: ignore

if __name__ == '__main__':
  unittest.main()