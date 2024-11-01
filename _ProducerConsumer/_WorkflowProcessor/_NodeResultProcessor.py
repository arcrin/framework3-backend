from _Node._BaseNode import BaseNode
import trio


class NodeResultProcessor:
    def __init__(
        self,
        receive_channel: trio.MemoryReceiveChannel[BaseNode],
        send_channel: trio.MemorySendChannel[BaseNode],
    ):
        self._receive_channel = receive_channel
        self._send_channel = send_channel

    # TODO: Write unit function for this
    async def start(self):
        async with trio.open_nursery() as nursery:
            async with self._receive_channel:
                async for node in self._receive_channel:
                    if node.result:
                        nursery.start_soon(node.set_cleared)
                    else:
                        nursery.start_soon(self._send_channel.send, node)


"""
The NodeResultProcessor class is structured to asynchronously handle nodes based on their results,
directing successful nodes to a clearance process and forwarding unsuccessful ones for further 
processing. Here are some suggestions and considerations to enhance its robustness, maintainability,
and effectiveness:
    1. Error Handling and Robustness
        - Specific Error Handling: Incorporate error handling specifically for the operations
        node.set_cleared and self._send_channel.send. These operations could fail due to various
        reasons, and handling these cases properly can prevent the processor from crashing and 
        ensure system stability.

        - Graceful Error Recovery: Consider what should happen if an error occurs. For instance, if 
        set_cleared fails, should the node be retired, logged, or sent to a different channel for further
        analysis? Implementing robust error recovery strategies can significantly enhance the resilience
        of your system.
        
    2. Concurrency and Resource Management
        - Resource Limits: Manage resources by potentially limiting the number of concurrent operations.
        If set_cleared or send are resource-intensive, managing concurrency can prevent resource exhaustion.

        - Handling of Channel Closures: Ensure that the closing of the send channel inside this process is
        handled gracefully, particularly in error conditions. If the send channel is closed unexpectedly,
        the system should properly log this event and either attempt to reopen the channel or shutdown 
        gracefully.

    3. Logging and Monitoring
        - Enhanced Logging: Log key actions and decisions, such as when a node is cleared, when it is 
        forwarded for further processing, and when any errors occur. This will aid in debugging and 
        operational monitoring.

        - Monitoring Node Processing: If feasible, implement monitoring to track how many nodes are
        processed, how many are cleared successfully, and how many fail. This data can be invaluable 
        for understanding system performance and identifying areas for improvement.

    4. Testing and Validation
        - Unit Testing: As noted in your TODO, writing unit tests for this functionality is crucial. 
        Test cases should cover successful node processing, handling of nodes that need further action,
        and error conditions in both set_cleared and send operations.

        - Integration Testing: Ensure that this component integrates smoothly with other parts of your
        system, particularly with the channels and node handling mechanisms. Test the processor under
        load to ensure it behaves as expected. 
"""