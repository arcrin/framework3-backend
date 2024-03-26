from _CommunicationModules._WSCommModule import WSCommModule
import json
import trio_websocket
import trio


class UIRequestProcessor:
    def __init__(
        self,
        ui_request_receive_channel: trio.MemoryReceiveChannel[str],
        ui_response_receive_channel: trio.MemoryReceiveChannel[str],
        comm_module: WSCommModule
    ):
        self._ui_request_receive_channel: trio.MemoryReceiveChannel[str] = ui_request_receive_channel
        self._ui_response_receive_channel: trio.MemoryReceiveChannel[str] = ui_response_receive_channel  
        self._comm_module: WSCommModule = comm_module

    @property
    def ws_connection(self) -> trio_websocket.WebSocketConnection:
        return self._ws_connection
    
    @ws_connection.setter
    def ws_connection(self, value: trio_websocket.WebSocketConnection) -> None:
        self._ws_connection = value 

    async def start(self):
        try:
            async with trio.open_nursery() as nursery:
                async for ui_request in self._ui_request_receive_channel:
                    await self._comm_module.ws_control_connection.send_message(json.dumps(ui_request.message))
                    response = await self._ui_response_receive_channel.receive()
                    ui_request.response = response
        except Exception as e:
            print(e)
            raise
 
