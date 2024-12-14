from _Node._BaseNode import BaseNode
import trio
import logging


class NodeExecutor:
    def __init__(
        self,
        receive_channel: trio.MemoryReceiveChannel[BaseNode],
        send_channel: trio.MemorySendChannel[BaseNode],
    ):
        self._receive_channel = receive_channel
        self._send_channel = send_channel
        self._logger = logging.getLogger("NodeExecutor")

    async def _execute_node(self, node: BaseNode):
        try:
            await node.execute()
            await self._send_channel.send(node)
        # TODO: Need to handle BrokenResourceError and CloseResourceError properly, need to make sure the application does not crash, and able to recover from channel related errors
        except Exception as e:
            self._logger.error(f"An error occurred while processing {node.name}: {e}")
            raise e

    async def start(self):
        async with trio.open_nursery() as nursery:
            async with self._receive_channel:
                async for node in self._receive_channel:
                    nursery.start_soon(self._execute_node, node) #TODO: how to handle cancellation?

    async def stop(self):
        await self._send_channel.aclose()

"""
Key Elements of NodeExecutor
1. Channels for Communication:
    - NodeExecutor uses Trio's MemoryReceiveChannel and MemorySendChannel to manage communication with other
    components in the system. This design allows it to act as a bridge between different workflow stages, 
    receiving nodes to execute and passing them along once complete.
2. Node Execution:
    - The core execution logic is in _execute_node, where each node's execute method is called.
    - After execution, the node is sent through the _send_channel, allowing downstream consumers to continue 
    processing it.
    - By using start_soon within a nursery in the start method, NodeExecutor allows concurrent execution of 
    multiple nodes, aligning with the parallel processing requirement.
3. Error Handling:
    - Basic error handling is implemented in _execute_node, where exceptions are logged. However, there's 
    a TODO note about handling BrokenResourceError and CloseResourceError for robustness. These errors are 
    specific to channel operations, and handling them would prevent application crashes due to communication
    issues.
4. Graceful Shutdown:
    - The stop method closes the _send_channel gracefully, ensuring no more nodes are sent after NodeExecutor
    stops.

Considerations for Improvement
1. Enhanced Error Handling:
    - Implementing custom handling for BrokenResourceError and ClosedResourceError will be essential to ensure
    the system remains stable. Possible actions could include:
        - Reconnecting or reopening channels if possible.
        - Implementing a retry mechanism to handle transient channel issues.
        - Logging detailed information to help identify and resolve channel issues.
2. Backpressure Management:
    - If there are scenarios where nodes are processed faster than they're sent downstream, or vice versa, 
    backpressure could become an issue. Using bounded channels with a buffer size or adding flow control 
    could help manage this.
3. Dynamic Node Routing:
    - Currently, all nodes are sent through the _send_channel after execution. If you plan to route nodes 
    to different consumers based on certain conditions (e.g., success vs. failure), consider adding 
    conditional routing logic within _execute_node.
4. Shutdown Strategy:
    - Asynchronous applications benefit from a coordinated shutdown strategy. you might want to ensure any
    pending nodes are fully processed or requeued before shutting down the NodeExecutor.

"""