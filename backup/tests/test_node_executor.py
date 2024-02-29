# type: ignore
from producer_consumer.node_executor import NodeExecutor
from unittest.mock import AsyncMock, MagicMock
from node.terminal_node import TerminalNode
from node.base_node import BaseNode
import unittest
import asyncio

class ConcreteNode(BaseNode):
  def __init__(self, name: str="Node") -> None:
    super().__init__(name)
    self._result = None
    
  async def execute(self):
    self._result = True

  @property
  def result(self):
    return self._result


class TestNodeExecutor(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        input_queue = MagicMock()
        output_queue = AsyncMock()
        self.node_executor = NodeExecutor(input_queue, output_queue)
        self.loop = asyncio.get_event_loop()

    def test_node_executor_init(self):
        input_queue = asyncio.Queue()
        output_queue = asyncio.Queue()
        node_executor = NodeExecutor(input_queue, output_queue)
        self.assertEqual(node_executor._input_queue, input_queue)
        self.assertEqual(node_executor._send_channel, output_queue)

    async def test_process_queue(self):
        input_queue = asyncio.Queue()
        output_queue = asyncio.Queue()
        node_executor = NodeExecutor(input_queue, output_queue)
        node1 = ConcreteNode("Node 1")
        node2 = ConcreteNode("Node 2")
        node3 = ConcreteNode("Node 3")
        node4 = ConcreteNode("Node 4")
        node5 = ConcreteNode("Node 5")

        nodes = [node1, node2, node3, node4, node5]

        for node in nodes:
            await input_queue.put(node)
        await input_queue.put(TerminalNode())

        # Start processing the queue
        await node_executor.process_queue()

        # Check that all nodes were processed and added to the output queue

        # The first node in the output queue should be the sentinel node
        output_sentinel_node = await output_queue.get()
        self.assertIsInstance(output_sentinel_node, TerminalNode)

        for node in nodes:
            output_node = await output_queue.get()
            self.assertEqual(node, output_node)


    async def test_process_queue_error_handling(self):
        input_queue = asyncio.Queue()
        output_queue = asyncio.Queue()
        node_executor = NodeExecutor(input_queue, output_queue)

        class ErrorNode(BaseNode):
            async def execute(self):
                raise Exception("Error")

            @property
            def result(self):
                return None
            
        await input_queue.put(ErrorNode())
        await input_queue.put(TerminalNode())

        # Start processing the queue and check that an error message is printed
        with self.assertRaises(Exception) as cm:
            await node_executor.process_queue()
        self.assertEqual(str(cm.exception), "Error")


if __name__ == "__main__":
    unittest.main()
