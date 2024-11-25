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
Key Elements in NodeResultProcessor
1. Channel-Based Communication:
    - Like the other workflow components, NodeResultProcessor uses channels for inter-component communication.
    It receive_channel and may send nodes to the next stage through send_channel.
2. Result-Based Decision Logic:
    - The component checks each node's result attribute:
        - If result is truthy: The node is marked as cleared by calling node.set_cleared, signifying it has passed 
        processing and can move forward.
        - If result is falsy: The node is sent to the next stage using _send_channel. This could signify a failed 
        result or a case where further processing is needed.
    - This result-based routing allows the system to handle nodes with different outcomes, enabling flexibility.
3. Concurrency Handling with Trio's Nursery:
    - The start method runs each action concurrently using nursery.start_soon, ensuring that multiple nodes can be 
    processed simultaneously. This concurrency aligns with the need for efficient handling in high-throughput environments.

Considerations for Improvement
1. Clarify result Evaluation Criteria:
    - Depending on what constitutes a valid or invalid result, you may want to make the check on result more explicit.
    - For instance, if result can be various data types or structures, you might add a helper function (e.g., is_valid_result)
    to centralize the validation logic and make it more readable.
2. Additional Result Routing
    - Currently, the processor either marks the node as cleared or sends it to the next stage. If more nuanced result 
    handling is required (e.g., redirecting nodes with warnings or partially successful results), consider expanding
    this routing logic.
    - For instance, you could introduce categories like "warning", "retry", or "log only" and route the nodes based
    on these categories.
3. Error Handling:
    - send_channel.send and set_cleared might fail under certain conditions. Adding error handling to log these issues 
    or retry specific actions could improve resilience.
    - For example:

            try:
                if node.result:
                    await node.set_cleared()
                else:
                    await self._send_channel.send(node)
            except Exception as e:
                # Log and handle the exception appropriately
        
4. Unit Testing (TODO):
    - The TODO in the code hints at the need for unit tests. You could mock the channels and node behaviors to validate 
    different outcomes, such as:
        - Verifying that set_cleared is called for nodes with valid results.
        - Checking that nodes with invalid results are passed to the send_channel.        
"""