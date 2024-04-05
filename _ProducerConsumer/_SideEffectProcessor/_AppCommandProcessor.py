from typing import Callable, Dict, Any
import logging
import trio

class AppCommandProcessor:
    def __init__(
            self,
            command_receive_channel: trio.MemoryReceiveChannel[Dict[Any, Any]],
            command_mapping: Dict[str, Callable[..., Any]]) :
        self._command_receive_channel = command_receive_channel
        self._command_mapping = command_mapping
        self._logger = logging.getLogger("AppCommandProcessor")

    async def start(self):
        try:
            async for command in self._command_receive_channel:
                self._logger.info(f"Command received: {command["command_type"]}")
                if command["command_type"] in self._command_mapping:
                    await self._command_mapping[command["command_type"]](**command["payload"])
                else:
                    self._logger.info(f"Command {command} not found")
        except Exception as e:
            self._logger.error(e)
            raise