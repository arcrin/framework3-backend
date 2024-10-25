from typing import Set
from trio_websocket import WebSocketConnection, ConnectionClosed  # type: ignore
from queue import Queue
from _Node._TestRunTerminalNode import TestRunTerminalNode
from _CommunicationModules._WSCommModule import WSCommModule
import json
import trio
import logging


class LogProcessor:
    def __init__(
        self,
        log_queue: Queue[
            logging.LogRecord | TestRunTerminalNode
        ],  # REMOVE: remove terminal node from the type
        comm_module: WSCommModule,
    ):
        self._log_queue = log_queue
        self._comm_module = comm_module
        self._cancel_scope: trio.CancelScope | None = None
        self._stop_flag = False
        self._logger = logging.getLogger("LogProcessor")    

    async def send_message(self, connection: WebSocketConnection, message: str):  # type: ignore
        try:
            await connection.send_message(message)  # type: ignore
        except ConnectionClosed:
            self._logger.error(
                f"Connection {connection} closed, removing from connection list"
            )

    async def start(self):
        formatter = logging.Formatter(
            "%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"
        )
        async with trio.open_nursery() as nursery:
            self._cancel_scope = nursery.cancel_scope
            while True:
                try:
                    record = await trio.to_thread.run_sync(self._log_queue.get)
                    if isinstance(record, TestRunTerminalNode):
                        break
                    message = formatter.format(record)
                    json_message = json.dumps({"type": "log", "message": message})
                    for connection in self._comm_module.all_ws_connection:
                        nursery.start_soon(self.send_message, connection, json_message)
                except trio.Cancelled:
                    self._logger.error("Log processor cancelled")
                    break
                await trio.sleep(0)

    def stop(self):
        # self._log_queue.put(TestRunTerminalNode())
        pass
