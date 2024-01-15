# type: ignore
import unittest
import asyncio
from producer_consumer.node_executor import NodeExecutor


class TestNodeExecutor(unittest.TestCase):
  def test_node_executor_init(self):
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()
    node_executor = NodeExecutor(input_queue, output_queue)
    self.assertEqual(node_executor._input_queue, input_queue)
    self.assertEqual(node_executor._output_queue, output_queue)

if __name__ == '__main__':
  unittest.main()