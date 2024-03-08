# type: ignore
import json
import trio_websocket
import trio


class UIRequestProcessor:
    def __init__(
        self,
        ui_request_receive_channel: trio.MemoryReceiveChannel[str],
        ui_response_receive_channel: trio.MemoryReceiveChannel[str],

    ):
        self._ui_request_receive_channel: trio.MemoryReceiveChannel = ui_request_receive_channel
        self._ui_response_receive_channel: trio.MemoryReceiveChannel = ui_response_receive_channel  
        self._ws_connection: trio_websocket.WebSocketConnection = None

    @property
    def ws_connection(self) -> trio_websocket.WebSocketConnection:
        return self._ws_connection
    
    @ws_connection.setter
    def ws_connection(self, value: trio_websocket.WebSocketConnection) -> None:
        self._ws_connection = value 

    async def start(self):
        async with trio.open_nursery() as nursery:
            async for ui_request in self._receive_channel:
                await self._ws_connection.send_message(json.dumps(ui_request.message))
                response = await self._ui_response_receive_channel.receive()
                ui_request.response = response
 
