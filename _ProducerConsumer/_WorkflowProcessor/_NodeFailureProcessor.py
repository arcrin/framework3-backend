from _Node._BaseNode import BaseNode
from _Node._TCNode import TCNode
import trio


class NodeFailureProcessor:
    def __init__(self, receive_channel: trio.MemoryReceiveChannel[BaseNode]) -> None:
        self._receive_channel = receive_channel

    async def start(self) -> None:
        async with trio.open_nursery() as nursery:
            async with self._receive_channel:
                async for node in self._receive_channel:
                    if isinstance(node, TCNode) and node.auto_retry_count > 0:
                        nursery.start_soon(node.check_dependency_and_schedule_self)
                    else:
                        if isinstance(node, TCNode):
                            nursery.start_soon(node.quarantine)

"""
Key Elements in NodeFailureProcessor
1. Channel for Failed Node Input:
    - NodeFailureProcessor listens on a receive_channel for nodes that have failed during processing. 
    This aligns with the producer-consumer model, where  it acts as a dedicated consumer for handling 
    node failures.
2. Conditional Retry or Quarantine Logic:
    - The component checks if the node is an instance of TCNode and whether auto_retry_count is greater 
    than zero.
        - Retries: If the node has retries left, NodeFailureProcessor calls check_dependency_and_schedule_self,
        which resets the nodes's dependencies and reschedules it for execution.
        - Quarantine: If retries are exhausted, the node is sent to quarantine by calling node.quarantine, 
        isolating it for review or further handling.
3. Concurrency with Trio's Nursery:
    - By using start_soon within a nursery, NodeFailureProcessor can handle multiple node failures concurrently. 
    This is particularly useful if several nodes fail simultaneously and need to be retried or quarantined without
    blocking each other.

Considerations for Improvement
1. Enhanced Retry Logic:
    - Exponential Backoff: To avoid rapid reattempts, consider implementing an exponential backoff for retries.
    This could be done by introducing a delay between retries, which would increase with each attempt.
    - Retry Limit: While auto_retry_count provides a retry limit, you could make this more dynamic by configuring 
    retry policies at runtime, allowing different nodes to have custom retry behavior.
2. Quarantine Handling:
    - Event Publishing: If quarantining a node triggers follow-up actions (e.g., alerts or logging), consider 
    publishing an event when a node is quarantined. This would allow other parts of the system respond to quarantined 
    nodes without hardcoding logic in NodeFailureProcessor.
    - Tracking Quarantined Nodes: Maintaining a log or database entry of quarantined nodes can provide valuable insights,
    especially if you want to analyze failure patterns later.
3. Error Handling and REsilience:
    - Graceful Failure: If an exception occurs while checking dependencies or quaranting, you might consider adding 
    error handling to prevent unhandled exceptions from affecting other processes.
    - Automatic Recovery: In the case of a temporary issue, like a network disruption affecting resource access, 
    consider an automatic recovery or retry mechanism to handle intermittent failures gracefully.
"""