from _Node._BaseNode import BaseNode
import trio

class ResultProcessor:
  def __init__(self, receive_channel: trio.MemoryReceiveChannel[BaseNode]):
    self._receive_channel = receive_channel

  # TODO: Write unit function for this
  async def start(self):
    async with trio.open_nursery() as nursery:
      async with self._receive_channel:
        async for node in self._receive_channel:
          if node.result:
            nursery.start_soon(node.set_cleared)