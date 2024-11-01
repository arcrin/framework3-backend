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
                    nursery.start_soon(self._execute_node, node)

    async def stop(self):
        await self._send_channel.aclose()


"""
The NodeExecutor class setup to process nodes by executing them asynchronously looks solid and
aligns well with a concurrent processing model using Trio. However, there are few enhancements
and error handling strategies that could improve its robustness and fault tolerance. Here's a 
breakdown of potential improvements:
    1. Improved Error Handling
        - Specific Exceptions: Instead of catching all exceptions broadly with Exception, focus 
        on catching specific exceptions that you expect might occur, such as trio.BrokenResourceError
        and trio.ClosedResourceError. This way, you can handle each type of error appropriately.

        - Error Recovery: Implement strategies for recovering from specific errors. For example, 
        if the send channel is closed unexpectedly (ClosedResourceError), you could log the error, 
        optionally attempt to reopen the channel, or shut down the executor gracefully.
        
    2. Resource Management
        - Graceful Shutdown: The stop method currently just closes the send channel. Ensure that this 
        method also handles any ongoing node processing gracefully. This could involve waiting for all 
        tasks in the nursery to complete before closing the channels.

        - Concurrency Control: If node.execute() is particularly resource-intensive, or if the system
        has limitations on how many nodes should be processed concurrently, consider adding a mechanism
        to limit the number of concurrent execute operations.

    3. Logging and Monitoring
        - Detailed Logging: Log more details about the nodes being processed, including success and
        failure outcomes. This crucial for debugging and understanding the system's behavior,
        especially during failures.

        - Monitoring: If your application's scale justifies it, consider implementing monitoring for 
        metrics like the number of nodes processed, processing times, and error rates.

    4. Testing and Reliability
        - Unit Testing: Write unit tets for the NodeExecutor to test both normal operation and error
        handling scenarios. Make sure to mock BaseNode.execute() and simulate both success and failure
        cases. 
        
        - Integration Testing: Test how NodeExecutor interacts with other components, particularly the 
        send and receive channels. Ensure it behaves correctly when channels are closed or when there 
        are network issues.

"""