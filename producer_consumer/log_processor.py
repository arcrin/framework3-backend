#type: ignore
from typing import Set
from trio_websocket import WebSocketConnection, ConnectionClosed #type: ignore
from queue import Queue
import trio
import logging


class LogProcessor:
    def __init__(self, 
                 log_queue: Queue[logging.LogRecord],
                 ws_connections: Set[WebSocketConnection]):
        self._log_queue = log_queue 
        self._ws_connections = ws_connections
        self._cancel_scope: trio.CancelScope = None

    async def send_message(self, connection, message):
        try:
            await connection.send_message(message)
        except ConnectionClosed:
            self._ws_connections.remove(connection)
            logging.error("Connection closed, removing from connection list")


    async def start(self):
        formatter = logging.Formatter("%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")
        self._cancel_scope = trio.CancelScope()
        with self._cancel_scope:
            async with trio.open_nursery() as nursery:
                while True:
                    record = await trio.to_thread.run_sync(self._log_queue.get) 
                    message = formatter.format(record)
                    for connection in self._ws_connections:
                        nursery.start_soon(self.send_message, connection, message)

    def stop(self):
        if self._cancel_scope is not None:
            self._cancel_scope.cancel()