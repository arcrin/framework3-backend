from node.base_node import BaseNode
from typing import List, Awaitable
import asyncio

class NodeExecutor:
  def __init__(self, input_queue: asyncio.Queue[BaseNode], output_queue: asyncio.Queue[BaseNode]):
    self._input_queue = input_queue
    self._output_queue = output_queue
    self._tasks: List[Awaitable[None]] = []

  
  async def _execute_node(self, node: BaseNode):
    await node.execute()
    await self._output_queue.put(node)

  async def process_queue(self):
    # TODO: this isn't executing test cases concurrently. I need to compare to the old implementation
    while True:
      node = await self._input_queue.get()
      task = asyncio.create_task(self._execute_node(node))
      self._tasks.append(task)

      # If the queue is empty, wait for all tasks to complete before continuing 
      if self._input_queue.empty():
        await asyncio.gather(*self._tasks)
        self._tasks = []


  def start_processing(self):
    return asyncio.create_task(self.process_queue())
      
    