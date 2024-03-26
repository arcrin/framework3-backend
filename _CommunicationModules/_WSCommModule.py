from trio_websocket import ConnectionClosed, serve_websocket, WebSocketRequest, WebSocketConnection # type: ignore
from typing import List, TYPE_CHECKING
# from datetime import datetime
# import hashlib
# import uuid
import logging
import json
import trio

if TYPE_CHECKING:
    from _Application._Application import Application


# TODO: all comm modules should implement an interface
class WSCommModule:
    def __init__(self, 
                 command_send_channel: trio.MemorySendChannel[str],
                 ui_response_send_channel: trio.MemorySendChannel[str],
                 app: "Application"):
        self._command_send_channel = command_send_channel
        self._ui_response_send_channel = ui_response_send_channel
        self._server_cancel_scope: trio.CancelScope | None = None    
        self._app = app
        self._logger = logging.getLogger("WSCommModule")



    @property
    def ws_control_connection(self):
        if self._app.control_session is not None:
            return self._app.control_session.connection
        else:
            self._logger.error("Control session not established")
            raise Exception("Control session not established")
    
    @property
    def all_ws_connection(self):
        return list(self._app.sessions.keys())

    async def ws_connection_handler(self, request: WebSocketRequest):
        ws = await request.accept() # type: ignore
        self._app.add_session(ws)
        self._logger.info(f"WS connection established with: {ws}")
        while True:
            try:
                message = await self._app.control_session.connection.get_message() # type: ignore
                data = json.loads(message) # type: ignore
                if data["type"] == "command":
                    if data["value"]  == "loadTC":
                        self._logger.info("loadTC command received")
                        await self._command_send_channel.send("loadTC")
                elif data["type"] == "ui-response":
                    await self._ui_response_send_channel.send(data["value"])

            except ConnectionClosed:
                self._logger.info(f"WS connection closed with {ws}") 
                self._app.remove_session(ws)
                break

    
    async def  start(self):
        self._server_cancel_scope = trio.CancelScope()
        try:
            with self._server_cancel_scope:
                await serve_websocket(self.ws_connection_handler, "localhost", 8000, ssl_context=None)
        except Exception as e:
            self._logger.error(e)
            raise
