from trio_websocket import ConnectionClosed, serve_websocket, WebSocketRequest, WebSocketConnection # type: ignore
from typing import List
# from datetime import datetime
# import hashlib
# import uuid
import logging
import json
import trio

# TODO: all comm modules should implement an interface
class WSCommModule:
    def __init__(self, 
                 command_send_channel: trio.MemorySendChannel[str],
                 ui_response_send_channel: trio.MemorySendChannel[str]):
        self._command_send_channel = command_send_channel
        self._ui_response_send_channel = ui_response_send_channel 
        self._ws_control_connection = None
        self._all_ws_connection: List[WebSocketConnection] = []
        self._server_cancel_scope: trio.CancelScope | None = None    
        self._logger = logging.getLogger("WSCommModule")


    @property
    def ws_control_connection(self):
        return self._ws_control_connection
    
    @property
    def all_ws_connection(self):
        return self._all_ws_connection

    async def ws_connection_handler(self, request: WebSocketRequest):
        ws = await request.accept() # type: ignore
        if not self._ws_control_connection:
            self._ws_control_connection = ws
        self._logger.info(f"WS connection established with: {ws}")
        # TODO: reconsider the necessity of adding a key to the connection
        # raw_key = f"{datetime.now().isoformat()}-{uuid.uuid4()}"
        # hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
        self._all_ws_connection.append(ws)
        while True:
            try:
                message = await self._ws_control_connection.get_message() # type: ignore
                data = json.loads(message) # type: ignore
                if data["type"] == "command":
                    if data["value"]  == "loadTC":
                        self._logger.info("loadTC command received")
                        await self._command_send_channel.send("loadTC")
                elif data["type"] == "ui-response":
                    await self._ui_response_send_channel.send(data["value"])

            except ConnectionClosed:
                self._logger.info(f"WS connection closed with {ws}") 
                if ws == self._ws_control_connection:
                    # TODO: how to hand over the control and which connection to hand the control to
                    self._ws_control_connection = None
                self._all_ws_connection.remove(ws)
                break

    
    async def  start(self):
        self._server_cancel_scope = trio.CancelScope()
        try:
            with self._server_cancel_scope:
                await serve_websocket(self.ws_connection_handler, "localhost", 8000, ssl_context=None)
        except Exception as e:
            self._logger.error(e)
            raise
