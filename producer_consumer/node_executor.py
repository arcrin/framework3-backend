from node.base_node import BaseNode
from node.terminal_node import TerminalNode
from typing import List
import trio


class NodeExecutor:
    def __init__(
        self,
        receive_channel: trio.MemoryReceiveChannel[BaseNode],
        send_channel: trio.MemorySendChannel[BaseNode]
    ):
        self._receive_channel = receive_channel
        self._send_channel = send_channel

    async def _execute_node(self, node: BaseNode):
        try:
          await node.execute()
          await self._send_channel.send(node)
        except Exception as e:
            # TODO: Handle the exception here
            print(f"An error occurred while executing node {node.name}: {e}")
            raise e


    async def process(self):
        async with trio.open_nursery() as nursery:
            async with self._receive_channel:
                async for node in self._receive_channel:
                    if isinstance(node, TerminalNode):
                        # TODO: Test this, make sure this is the proper way to terminate this function
                        await self._send_channel.aclose()
                        return
                    else:
                        nursery.start_soon(self._execute_node, node)