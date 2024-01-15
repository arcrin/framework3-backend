from node.base_node import BaseNode
from node.executable_node import ExecutableNode
from node.load_test_case_node import LoadTestCaseNode
from typing import Union
import asyncio

class NodeExecutor:
  def __init__(self, input_queue: asyncio.Queue[BaseNode], output_queue: asyncio.Queue[BaseNode]):
    self._input_queue = input_queue
    self._output_queue = output_queue

  
  async def _execute_node(self, node: Union[LoadTestCaseNode, ExecutableNode]):
    await node.execute()
    await self._output_queue.put(node)

  async def process_queue(self):
    while True:
      node = await self._input_queue.get()
      if isinstance(node, ExecutableNode) or isinstance(node, LoadTestCaseNode):
        await self._execute_node(node)

  def start_processing(self):
    return asyncio.create_task(self.process_queue())
      
    