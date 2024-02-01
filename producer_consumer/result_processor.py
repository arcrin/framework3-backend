from node.sentinel_node import SentinelNode
from node.base_node import BaseNode
import asyncio

class ResultProcessor:
  def __init__(self, input_queue: asyncio.Queue[BaseNode]):
    self._input_queue = input_queue


  async def process_queue(self):
    while True:
      node = await self._input_queue.get()
      if isinstance(node, SentinelNode):
        return
      if node.result:
        await node.set_cleared()

  def start_processing(self):
    return asyncio.create_task(self.process_queue())