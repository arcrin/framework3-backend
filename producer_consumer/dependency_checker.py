from node.base_node import BaseNode
from typing import List
import asyncio

class DependencyChecker:
  def __init__(self, node_list: List[BaseNode], output_queue: asyncio.Queue[BaseNode]) -> None:
    self._output_queue = output_queue
    self._node_list = node_list

  async def process_queue(self):
    while True:
      try:
        for node in self._node_list:
          if node.is_cleared():
            await self._output_queue.put(node)
      except Exception as e:
        print(f"DependencyChecker Exception: {e}")
      await asyncio.sleep(1)

  def start_processing(self):
    return asyncio.create_task(self.process_queue())
  