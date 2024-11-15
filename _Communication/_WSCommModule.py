from trio_websocket import ( # type: ignore
    ConnectionClosed,
    serve_websocket, # type: ignore
    WebSocketRequest,
    WebSocketConnection, # type: ignore
)  
from typing import TYPE_CHECKING
import logging
import json
import trio

if TYPE_CHECKING:
    from _Application._AppStateManager import ApplicationStateManager


# TODO: all comm modules should implement an interface
class WSCommModule:
    def __init__(
        self,
        command_send_channel: trio.MemorySendChannel[str],
        ui_response_send_channel: trio.MemorySendChannel[str],
        asm: "ApplicationStateManager",
    ):
        self._command_send_channel = command_send_channel
        self._ui_response_send_channel = ui_response_send_channel
        self._server_cancel_scope: trio.CancelScope | None = None
        self._asm = asm
        self._logger = logging.getLogger("WSCommModule")

    @property
    def ws_control_connection(self):
        if self._asm.control_session is not None:
            return self._asm.control_session.connection
        else:
            self._logger.error("Control session not established")
            raise Exception("Control session not established")

    @property
    def all_ws_connection(self):
        return list(self._asm.sessions.keys())
    
    def remove_connection(self, ws_connection: WebSocketConnection):
        self._asm.remove_session(ws_connection)

    async def ws_connection_handler(self, request: WebSocketRequest):
        ws = await request.accept()  # type: ignore
        await self._asm.add_session(ws)
        self._logger.info(f"WS connection established with: {ws}")
        while True:
            try:
                message = await self._asm.control_session.connection.get_message()  # type: ignore
                data = json.loads(message)  # type: ignore
                if data["type"] == "command":
                    await self._command_send_channel.send(data)
                elif data["type"] == "ui-response":
                    await self._ui_response_send_channel.send(data["payload"])

            except ConnectionClosed:
                self._logger.info(f"WS connection closed with {ws}")
                self.remove_connection(ws)
                break

    async def start(self):
        self._server_cancel_scope = trio.CancelScope()
        try:
            with self._server_cancel_scope:
                await serve_websocket(
                    self.ws_connection_handler, "localhost", 8000, ssl_context=None
                )
        except Exception as e:
            self._logger.error(e)
            raise
