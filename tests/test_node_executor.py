# type: ignore
import unittest
import asyncio
from producer_consumer.node_executor import NodeExecutor
from unittest.mock import AsyncMock, MagicMock


class TestNodeExecutor(unittest.TestCase):
  def setUp(self):
    input_queue = MagicMock()
    output_queue = AsyncMock()
    self.node_executor = NodeExecutor(input_queue, output_queue)

  def test_node_executor_init(self):
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()
    node_executor = NodeExecutor(input_queue, output_queue)
    self.assertEqual(node_executor._input_queue, input_queue)
    self.assertEqual(node_executor._output_queue, output_queue)

  async def test_process_queue(self):
    # Mock the get method to return a dummy node
    dummy_node = object()
    self.node_executor._input_queue.get = AsyncMock(return_value=dummy_node)

    # Run the process_queue method in a separate task because it's an infinite loop
    task = asyncio.create_task(self.node_executor.process_queue())

    # Give the task a moment to start and call _execute_node
    await asyncio.sleep(0.1)

    # Cancel the task to stop the infinite loop
    task.cancel()

    # Assert that the task was cancelled
    self.node_executor._execute_node.assert_awaited_with(dummy_node)



if __name__ == '__main__':
  unittest.main()