from producer_consumer.result_processor import ResultProcessor
from node.base_node import BaseNode
import unittest
import asyncio


class PassNode(BaseNode):
  def __init__(self, name:str):
    super().__init__(name)

  async def execute(self):
    self._result = True

  @property
  def result(self):
    return self._result
  
class FailNode(BaseNode):
  def __init__(self, name:str):
    super().__init__(name)

  async def execute(self):
    self._result = False

  @property
  def result(self):
    return self._result

class TestResultProcessor(unittest.IsolatedAsyncioTestCase):
  async def test_process_queue(self):
    queue: asyncio.Queue[BaseNode] = asyncio.Queue()
    node1 = PassNode("node1")
    node2 = FailNode("node2")

    await node1.execute()
    await node2.execute()

    await queue.put(node1)
    await queue.put(node2)
    processor = ResultProcessor(queue)
    task = asyncio.create_task(processor.process_queue())

    await asyncio.sleep(0.1)

    task.cancel()

    self.assertTrue(node1.is_cleared())
    self.assertFalse(node2.is_cleared())


if __name__ == '__main__':
  unittest.main()