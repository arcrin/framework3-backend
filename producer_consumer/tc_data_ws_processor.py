from typing import Dict
import trio_websocket # type: ignore
import json
import trio


class TCDataWSProcessor:
    def __init__(self, tc_data_receive_channel: trio.MemoryReceiveChannel[Dict[str, str]]):
        self._tc_data_receive_channel: trio.MemoryReceiveChannel[Dict[str, str]] = tc_data_receive_channel
        self._ws_connection: trio_websocket.WebSocketConnection | None = None

    @property
    def ws_connection(self) -> trio_websocket.WebSocketConnection | None:
        return self._ws_connection
    
    @ws_connection.setter
    def ws_connection(self, value: trio_websocket.WebSocketConnection) -> None:
        self._ws_connection = value

    async def start(self):
        try:
            async with trio.open_nursery() as nursery: # type: ignore
                async for tc_data in self._tc_data_receive_channel:
                    await self._ws_connection.send_message(json.dumps(tc_data)) # type: ignore
        except Exception as e:
            print(e)
            raise