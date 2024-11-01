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
LogProcessor class is structured to handle logging messages asynchronously and send them to
WebSocket connections, which is a great approach for real-time log monitoring in distrubuted 
systems. Here are some enhancements and corrections to consider for making this component more
robust and efficient:

1. Error Handling and Connection Management
    - Connection Handling: Improve the way you handle closed connections. Currently, you log an 
    error when a connection is closed, but you should also remove the closed connection from the
    all_ws_connection list maintained by the WSCommModluel.
    
    - Error Handling in Message Sending: Consider what should happen if send_message fails. You
    may want to retry sending the message, log the failure, or take other corrective actions
    depending on your application's needs.

2. Queue Management
    - Queue Blocking: The current implementation blocks until an item is available in the queue. 
    This might be inefficient, specially if you have periods of low log activity. Consider 
    implementing a timeout or using a non-blocking queue approach.

    - Graceful Shutdown: Your method for stopping the log processor (stop) is currently empty and 
    commented out. Implement a mechanism to signal the start loop to exit gracefully, perhaps by 
    setting a flag or using a special log record that indicates shutdown.
    
3. Log Formatting and Transmission
    - Efficient Formatting: Consider moving the creation of the formatter outside of the start method 
    if it doesn't change over time. This saves the overhead of recreating if on each call.  
    
    - Message Construction: Ensure that the JSON encoding of log message does not fail due to unserializable
    objects in the log records. Customize the formatter or the serialization process to handle complex objects
    gracefully

4. Performance Considerations
    - Asynchronous Queue: Using a synchronous queue (Queue) and running it in a thred via trio.to_thread.run_sync
    might not be efficient approach. Consider using trio's native channels (trio.MemoryChannel) for better 
    performance and integration with async operations.

5. Testing and Robustness
    - Testing: Add comprehensive unit and integration tests for the log processing functionality. Ensure you test
    scenarios including rapid logging, connection failures, and graceful shutdowns.
"""