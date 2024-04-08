from _Node._BaseNode import BaseNode
import trio


class NodeResultProcessor:
    def __init__(
        self,
        receive_channel: trio.MemoryReceiveChannel[BaseNode],
        send_channel: trio.MemorySendChannel[BaseNode],
    ):
        self._receive_channel = receive_channel
        self._send_channel = send_channel

    # TODO: Write unit function for this
    async def start(self):
        async with trio.open_nursery() as nursery:
            async with self._receive_channel:
                async for node in self._receive_channel:
                    if node.result:
                        nursery.start_soon(node.set_cleared)
                    else:
                        nursery.start_soon(self._send_channel.send, node)
