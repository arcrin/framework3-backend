from _Node._BaseNode import BaseNode
from _Node._TCNode import TCNode
import trio


class NodeFailureProcessor:
    def __init__(self, receive_channel: trio.MemoryReceiveChannel[BaseNode]) -> None:
        self._receive_channel = receive_channel

    async def start(self) -> None:
        async with trio.open_nursery() as nursery:
            async with self._receive_channel:
                async for node in self._receive_channel:
                    if isinstance(node, TCNode) and node.auto_retry_count > 0:
                        nursery.start_soon(node.check_dependency_and_schedule_self)
