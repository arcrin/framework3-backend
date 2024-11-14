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


"""
Passing comm_module into LogProcessor is definitely a step toward decoupling, as it separates the WebSocket implementation 
from the logging itself. However, there are more ways to make this separation more distinct, especially if you foresee 
needing to swap out WebSocket broadcasting or add alternative message broadcasting mechanisms. 

Why Further Decoupling?
1. Single Responsibility: Right now, LogProcessor is responsible for both log message formatting and message broadcasting.
Separating broadcasting would allow LogProcessor to focus exclusively on processing and formatting log messages, while
a dedicated broadcaster handles all message delivery.

2. Easier Future Change: If you ever need to add an alternative channel (e.g., saving log to a database or sending log to
other clients), having a dedicated MessageBroadcaster class would allow these changes without modifying LogProcessor.

3. Cleaner WebSocket Management: If WSCommModule or WebSocket management itself changes, further decoupling would isolate
changes within the broadcasting class instead of impacting the LogProcessor.

Sample Implementation:
Step 1: Define a MessageBroadcaster

    class MessageBroadcaster:
        def __init__(self, comm_module: WSCommModule):
            self._comm_module = comm_module
            self._logger = logging.getLogger("MessageBoardcaster")
        
        async def broadcast(self, message: str):
            for connection in self._comm_module.all_ws_connection:
                try:
                    await connection.send_message(message)
                except ConnectionClosed:
                    self._logger.error(f"Connection {connection} closed, removing from connection list)
                    self._comm_module.all_ws_connection.remove(connection)

Step 2: Update LogProcessor to Use MessageBroadcaster

    class LogProcessor:
        def __init__(self, log_queue: Queue[logging.LogRecord], broadcaster: MessageBroadcaster):
            self._log_queue = log_queue
            self._broadcaster = broadcaster
            self._stop_flag = False
            self._logger = logging.getLogger("LogProcessor")

        async def start(self):
            formatter = logging.Formatter("%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")
            async with trio.open_nursery() as nursery:
                while not self._stop_flag:
                    try:
                        if not self._log_queue.empty():
                            record = await trio.to_thread.run_sync(self._log_queue.get)
                            message = formatter.format(record)
                            json_message = json.dumps({"type": "log", "message": message})
                            nursery.start_soon(self._broadcaster.broadcast, json_message)
                        else:
                            await trio.sleep(0.1)
                    except trio.sleep(0.1)
                        self._logger.info("Log processor cancelled")
                        break

With this setup:
    - LogProcessor only formats the message and hands if off to MessageBroadcaster
    - MessageBroadcaster manages WebSocket connections and sends messages, providing a cleaner, single-purpose interface.

This approach here resembles Mediator Pattern. In this setup, MessageBroadcaster acts as an intermediary between LogProcessor 
and WSCommModule, coordinating communication without requyiring direct coupling between the logging logic and the communication
logic.

Key Characteristics of the Mediator Pattern
- Decoupling Components: The Mediator reduces dependencies between classes by centralizing communication. Here, LogProcessor 
only interacts with MessageBroadcaster, and MessageBroadcaster then ahndles the specifics of sending messages through WSCommModule.
- Single Responsibility: Each component maintains a focused responsibility. LogProcessor focuses solely on log processing, while 
MessageBroadcaster manages message distribution.
- Scalability and Flexibility: The mediator (i.e., MessageBroadcaster) enables easy scaling. For instance, if you later add file 
logging, database logging, or other types of communication, they could be additional methods in MessageBroadcaster without modifying 
LogProcessor.

When to use the Mediator Pattern
This pattern is particularly useful when:
- You need to centralize control or logic that involves multiple classes.
- Direct communication between components would create complex interdependencies.
- Components need to work together but should remain as independent and reusable as possible.
"""