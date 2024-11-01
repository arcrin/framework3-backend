from typing import Dict
from _CommunicationModules._WSCommModule import WSCommModule
import trio_websocket # type: ignore
import logging
import json
import trio


class TCDataWSProcessor:
    def __init__(self, 
                 tc_data_receive_channel: trio.MemoryReceiveChannel[Dict[str, str]],
                 comm_module: WSCommModule):
        self._tc_data_receive_channel: trio.MemoryReceiveChannel[Dict[str, str]] = tc_data_receive_channel
        self._comm_module: WSCommModule = comm_module
        self._logger = logging.getLogger("TCDataWSProcessor")

    async def start(self):
        try:
            async with trio.open_nursery() as nursery: # type: ignore
                async for tc_data in self._tc_data_receive_channel:
                    for connection in self._comm_module.all_ws_connection:  
                        try:
                            await connection.send_message(json.dumps(tc_data)) # type: ignore
                        except trio_websocket.ConnectionClosed as e:
                            self._logger.error(f"WS connection closed with {connection}")
                            self._comm_module.remove_connection(connection)
        except Exception as e:
            self._logger.error(e)
            raise
        
    """
    The TCDataWSProcessor class you've defined is set up to handle test case data from a channel and
    transmit this data over WebSocket connections managed by WSCommModule. This design fits well for
    real-time data streaming to clients. Here are some enhancement and considerations to improve the
    robustness, performance, and maintainability of this component.

    1. Error Handling and Connection Management
        - Error Handling in Connection Iteration: When iterating over connection to send messages, 
        handle the case where a connection might close during the iteration. This involves not only    
        catching the ConnectionClosed exception but also safely continuing to the next connection
        without disrupting the loop.

        - Retry Failed Transmissions: Consider implementing a retry mechanism for failed transmissions. 
        Depending on the requirements, you might retry immediately, or enqueue the data ro later retry.

        - Graceful Handling of Connection Issues: Ensure that the processor can handle losing all its
        WebSocket connections without crashing and can continue to function as connections are restored.
        
    2. Logging and Diagnostics
        - Detailed Logging: Include more detailed logging to help diagnose issues. Log Successful sends
        as well as failures. COnsider logging the content being send if it does not contain sensitive
        information.

        - Monitor and Alert: Implement monitoring for the number of active connections and alert if the 
        number drops below a certain threshold or if error rates spike.
     
    3. Resource and Concurrency Management
        - Concurrency Control: Managing how data is sent to potentially many connections simultaneously 
        is crucial. You might to control concurrency to prevent overwhelming the server or the network.

        - Efficient JSON handling: Since you're serializing data to JSON every connection, consider
        optimizing this by serizlizing once per data item, not once per connection.

    4. Testing and Reliability
        - Unit and Integration Testing: Ensure that there are comprehensive tests covering the functionality
        of this class. This includes tests for normal operation, handling of connection issues, and system
        behavior under high load.

        - Handling of Channel Closures: Ensure that the closure of _tc_data_receive_channel is handled 
        gracefully, allowing for clean shutdown or restart as necessary.

    """