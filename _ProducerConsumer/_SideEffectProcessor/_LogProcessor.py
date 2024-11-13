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
        log_queue: Queue[ logging.LogRecord | TestRunTerminalNode ],  # REMOVE: remove terminal node from the type
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
                    if self._log_queue:
                        record = await trio.to_thread.run_sync(self._log_queue.get)
                        if isinstance(record, TestRunTerminalNode):
                            break
                        message = formatter.format(record)
                        json_message = json.dumps({"type": "log", "message": message})
                        for connection in self._comm_module.all_ws_connection:
                            nursery.start_soon(self.send_message, connection, json_message)
                    else:
                        await trio.sleep(0.1) # prevent busy loop when queue is empty 
                except trio.Cancelled:
                    self._logger.error("Log processor cancelled")
                    break

    def stop(self):
        # self._log_queue.put(TestRunTerminalNode())
        pass
"""
Key Elements in LogProcessor
1. Log Queue for Processing Records:
    - LogProcessor listens on a queue, receiving LogRecord items (and potentially TestRunTerminalNode, though 
    it's noted to be removed) that it processes asynchronously.
    - Using a queue allows LogProcessor to decouple itself from the source of logs, supporting a flexible and
    non-blocking design.
2. WebSocket Communication:
    - It uses a WebSocket communication module (WSCommModule) to broadcast log messages to connected clients.
    - Each log message is formatted and converted into JSON before being sent to all active WebSocket connections,
    allowing real-time log monitoring.
3. Message Formatting:
    - A Formatter is used to convert LogRecord items into readable log messages.
    - The formatted messages are then serialized to JSON, adding a "type": "log" field, making them distinguishable
    from other potential WebSocket messages.
4. Graceful Shutdown:
    - The start method contains a loop that continues until TestRunTerminalNode is received (though this seems likely 
    to be removed based on your note) or until it's cancelled.
    - The stop method is currently empty, but should ideally provide a way to stop LogProcessor cleanly, allowing any
    remaining logs to be processed and connections to close gracefully.

Suggestions to Clarify and Simplify LogProcessor
1. Decouple WebSocket from Logging Logic:
    - To reduce coupling, consider separating the WebSocket broadcast functionality from LogProcessor, delegating it 
    to a more generic MessageBroadcaster.
    - LogProcessor could then focus on log processing, while MessageBroadcaster takes care of managing WebSocket 
    connections and sending messages.
2. Rethink Queue-Based Termination:
    - instead of passing a TestRunTerminalNode to signal termination, consider using a flag or dedicated shutdown
    event. This approach would make it clearer and prevent dependency on specific node types.
    - For example, you could use an internal _stop_flag (already defined) in combination with the stop method to 
    manage shutdown.
3. Improve Resilience for WebSocket Communication:
    - Add handling to remove broken connections from the connection list. If a connection closes unexpectedly, the 
    send_message method could catch this and remove the connection from _comm_module.all_ws_connection.
4. Implement Backpressure Management:
    - If log messages are generated faster than they can be sent, consider limiting the queue size or batching messages. 
    This could help prevent performance issues during high logging activity.
5. finalize the stop Method:
    - The stop method should set _stop_flag to True and possibly wake the processor if it's sleeping.
    - For a graceful shutdown, any remaining messages in the queue should be processed, and WebSocket connections 
    should be closed cleanly.

        class LogProcessor:
            ...
            async def start(self):
                formatter = logging.Formatter("%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")
                async with trio.open_nursery() as nursery:
                    self._cancel_scope = nursery.cancel_scope
                    while not self._stop_flag:
                        try: 
                            if not self._log_queue.empty():
                                record = await trio.to_thread.run_async(self._log_queue.get)
                                message = formatter.format(record)
                                json_message = json.dumps({"type": "log", message": message})
                                for connection in self._comm_module.all_ws_connection:
                                    nursery.start_soon(self.send_message, connection, json_message)
                            else:
                                await trio.sleep(0.1)
                        except trio.Cancelled:
                            self._logger.info("Log processor cancelled")
                            break
            
            def stop(self):
                self._stop_flag = True
                self._cancel_scope.cancel()

Overall Organization of Side Effect Processors
    - Consider grouping similar processors together and giving each a clear role. LogProcessor, for example, could be 
    classified under a logging module, classified under a logging module, while a UserInteractionProcessor could handle
    user-related interactions. Clear separation will help make each side effect processor's role more intuitive and 
    manageable. 
"""