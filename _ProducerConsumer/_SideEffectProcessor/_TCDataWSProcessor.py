from typing import Dict
from _CommunicationModules._WSCommModule import WSCommModule
import trio_websocket # type: ignore
import logging
import json
import trio


class TCDataWSProcessor:
    def __init__(self, 
                 tc_data_receive_channel: trio.MemoryReceiveChannel[Dict[str, str]],
                 comm_module: WSCommModule):
        self._tc_data_receive_channel: trio.MemoryReceiveChannel[Dict[str, str]] = tc_data_receive_channel
        self._comm_module: WSCommModule = comm_module
        self._logger = logging.getLogger("TCDataWSProcessor")

    async def start(self):
        try:
            async with trio.open_nursery() as nursery: # type: ignore
                async for tc_data in self._tc_data_receive_channel:
                    for connection in self._comm_module.all_ws_connection:  
                        try:
                            await connection.send_message(json.dumps(tc_data)) # type: ignore
                        except trio_websocket.ConnectionClosed as e:
                            self._logger.error(f"WS connection closed with {connection}")
                            self._comm_module.remove_connection(connection)
        except Exception as e:
            self._logger.error(e)
            raise
        
"""
As with LogProcessor, use a MessageBroadcaster as a communication mediator. Create a broadcast_test_case_results() method
for this purpose.
"""