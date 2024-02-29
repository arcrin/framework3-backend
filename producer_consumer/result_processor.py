from node.terminal_node import TerminalNode
from node.base_node import BaseNode
import trio

class ResultProcessor:
  def __init__(self, receive_channel: trio.MemoryReceiveChannel[BaseNode]):
    self._receive_channel = receive_channel

  # TODO: Write unit function for this
  async def process(self):
    async with trio.open_nursery() as nursery:
      async with self._receive_channel:
        async for node in self._receive_channel:
          if node.result:
            await node.set_cleared()