from _Application._SystemEvent import UserResponseEvent
from _Application._SystemEventBus import SystemEventBus
import trio
import logging

class UIResponseProcessor:
    def __init__(self, response_receive_channel: trio.MemoryReceiveChannel[str]):
        self._response_receive_channel = response_receive_channel
        self._logger = logging.getLogger("UIResponseProcessor")

    async def start(self):
        try:
            async with trio.open_nursery() as nursery:
                async for response in self._response_receive_channel:
                    self._logger.info(f"Received response: {response}")
                    nursery.start_soon(SystemEventBus.publish, UserResponseEvent(response)) # type: ignore
        except Exception as e:
            print(e)
            raise

"""
Key Elements in UIResponseProcessor
1. Channel-Based Response Reception:
    - UIResponseProcessor listens on response_receive_channel for user responses. This approach decouples the source
    of responses from the processor itself, aligning well with the producer-consumer pattern.
    
2. Event Publication via SystemEventBus:
    - Once a response is received, it's published as a UserResponseEvent using SystemEventBus. This event-driven approach
    enables any part of the application that subscribes to UserResponseEvent to react to user responses, making it a flexible
    way to handle asynchronous UI inputs.

3. Logging:
    - Each response is logged, providing traceability and helping with debugging or monitoring response flows.
    
Suggestions for Improvement
1. Abstract ZDependency on SystemEventBus:
    - Like other processors, you could consider using an event publishing interface or a centralized MessageBroadcaster. This
    would allow flexibility in how responses are handled and decouple UIResponseProcessor from SystemEventBus.
    - For instance, if responses need to be forwarded to multiple systems in the future, using a broadcasting interface would 
    allow this without modifying UIResponseProcessor.
    
2. Enhanced Error Handling:
    - Currently, any exception is logged and re-raised, which stops the processor. If resilience is essential, you could implement 
    a retry mechanism or log the error without interrupting the processor.
    - For example:
        except Exception as e:
            self._logger.error(f"Error processing response: {e}")

3. Graceful Shutdown:
    - While Trio will handle cancellation gracefully, adding a stop method closes the channel or sets a flag might make the shutdown 
    process clearer and ensure all resources are freed  properly.

4. Response Validation:
    - If responses are expected to follow a specific format or contain certain data, you could add basic validation before publishing 
    the event. This would prevent unintended or malformed responses from triggering system events.

Updated UIResponseProcessor with Optional Abstraction

    class UIResponseProcessor:
        def __init__(self, response_receive_channel: trio.MemoryReceiveChannel[str], event_publisher):
            self._response_receive_channel = response_receive_channel
            self._event_publisher = event_publisher
            self._logger = logging.getLogger("UIResponseProcessor")

        async def start(self):
            try:
                async with trio.open_nursery() as nursery:
                    async for response in self._response_receive_channel:
                        self._logger.info(f"Received response: {response}")
                        nursery.start_soon(self._event_publisher.publish, UserResponseEvent(response))
            except Exception as e:
                self._logger.error(f"Error in UIResponseProcessor: {e}")

"""