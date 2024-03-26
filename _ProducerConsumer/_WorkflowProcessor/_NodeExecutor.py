from _Node._BaseNode import BaseNode
from _Node._TerminalNode import TerminalNode
import trio
import logging


class NodeExecutor:
    def __init__(
        self,
        receive_channel: trio.MemoryReceiveChannel[BaseNode],
        send_channel: trio.MemorySendChannel[BaseNode]
    ):
        self._receive_channel = receive_channel
        self._send_channel = send_channel
        self._logger = logging.getLogger("NodeExecutor")

    async def _execute_node(self, node: BaseNode):
        try:
          await node.execute()
          await self._send_channel.send(node)
        #TODO: Need to handle BrokenResourceError and CloseResourceError properly, need to make sure the application does not crash, and able to recover from channel related errors
        except Exception as e:
            self._logger.error(f"An error occurred while processing {node.name}: {e}")
            raise e

    async def start(self):
        async with trio.open_nursery() as nursery:
            async with self._receive_channel:
                async for node in self._receive_channel:
                    if isinstance(node, TerminalNode):
                        await self.stop()
                        return
                    else:
                        nursery.start_soon(self._execute_node, node)

    async def stop(self):
        await self._send_channel.aclose()