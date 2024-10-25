from _Application._SystemEvent import UserResponseEvent
from _Application._SystemEventBus import SystemEventBus
import trio
import logging

class UIResponseProcessor:
    def __init__(self, response_receive_channel: trio.MemoryReceiveChannel[str]):
        self._response_receive_channel = response_receive_channel
        self._logger = logging.getLogger("UIResponseProcessor")

    async def start(self):
        try:
            async with trio.open_nursery() as nursery:
                async for response in self._response_receive_channel:
                    self._logger.info(f"Received response: {response}")
                    nursery.start_soon(SystemEventBus.publish, UserResponseEvent(response)) # type: ignore
        except Exception as e:
            print(e)
            raise
