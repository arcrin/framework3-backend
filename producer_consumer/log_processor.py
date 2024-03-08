#type: ignore
from typing import Set
from trio_websocket import WebSocketConnection, ConnectionClosed #type: ignore
from queue import Queue
from node.terminal_node import TerminalNode
import json
import trio
import logging


class LogProcessor:
    def __init__(self, 
                 log_queue: Queue[logging.LogRecord | TerminalNode],
                 ws_connections: Set[WebSocketConnection]):
        self._log_queue = log_queue 
        self._ws_connections = ws_connections
        self._cancel_scope: trio.CancelScope = None
        self._stop_flag = False 

    async def send_message(self, connection, message):
        try:
            await connection.send_message(message)
        except ConnectionClosed:
            self._ws_connections.remove(connection)
            logging.error("Connection closed, removing from connection list")


    async def start(self):
        formatter = logging.Formatter("%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")
        async with trio.open_nursery() as nursery:
            self._cancel_scope = nursery.cancel_scope
            while True:
                try:
                    record = await trio.to_thread.run_sync(self._log_queue.get) 
                    if isinstance(record, TerminalNode):
                        break   
                    message = formatter.format(record)
                    json_message = json.dumps({"type": "log", "message": message})
                    for connection in self._ws_connections:
                        nursery.start_soon(self.send_message, connection, json_message)
                except trio.Cancelled:
                    print("Log processor cancelled")
                    break
                await trio.sleep(0)

    def stop(self):
        self._log_queue.put(TerminalNode())