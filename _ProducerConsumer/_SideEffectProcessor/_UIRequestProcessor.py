from _Communication._WSCommModule import WSCommModule
from typing import TYPE_CHECKING
import json
import trio_websocket  # type: ignore
import trio
import logging

if TYPE_CHECKING:
    from util._InteractionContext import InteractionContext


class UIRequestProcessor:
    def __init__(
        self,
        ui_request_receive_channel: trio.MemoryReceiveChannel["InteractionContext"],
        comm_module: WSCommModule,
    ):
        self._ui_request_receive_channel: trio.MemoryReceiveChannel["InteractionContext"] = (
            ui_request_receive_channel
        )
        # self._ui_response_receive_channel: trio.MemoryReceiveChannel[str] = (
        #     ui_response_receive_channel
        # )
        self._comm_module: WSCommModule = comm_module
        self._logger = logging.getLogger("UIRequestProcessor")
        

    async def start(self):
        try:
            async with trio.open_nursery() as nursery:  # type: ignore
                async for interaction_context in self._ui_request_receive_channel:
                    await self._comm_module.ws_control_connection.send_message(  # type: ignore
                        json.dumps({
                            "type": "app_state",
                            "event_type": "prompt",
                            "payload": {
                                "id": interaction_context.id,
                                "message": interaction_context.message,
                                "prompt_type": interaction_context.interaction_type.value
                            }
                        })  # type: ignore
                    )
                    # COMMENT: I need some kind of "waiting" capability if I only want to handle one interaction at a time
                    # but I don't want to interact with another channel directly here
                    # response = await self._ui_response_receive_channel.receive()
                    # interaction_context.response = response  # type: ignore
                    await interaction_context.response_ready()
        except trio_websocket.ConnectionClosed as e:
            self._logger.error(f"WS connection closed with {self._comm_module.ws_control_connection}")
            raise
        except Exception as e:
            print(e)
            raise

"""
Key Elements of UIRequestProcessor
1. Receiving User Interface Requests:
    - UIResponseProcessor listens on ui_request_receive_channel for InteractionContext objects. This 
    design lets it process UI requests asynchronously, aligning with the producer-consumer mode.

2. WebSocket Communication for UI Prompts:
    - The processor uses WSCommModule to send InteractionContext data (like ID, message, and prompt type) 
    to the user interface
    - It packages the InteractionContext dta into JSOn format, specifying a "type": "app_state" and 
    "event_type": "prompt". This structure suggests that the UI will interpret the message to display
    prompts or other interactive elements.

3. Handling Interaction Responses:
    - There's a comment about requiring a "waiting" mechanism to process one interaction at a time without 
    directly interacting with another channel. This implies a need for synchronous handling of responses, 
    possibly to ensure that only one prompt is handled at any moment.

4. Graceful Error Handling:
    - If the WebSocket connection closes unexpectedly, UIRequestProcessor logs the issue and raises an exception.
    This keeps the process aware of any connection issues.

Suggestions for Improvement
1. Decouple WSCommModule Dependency:
    - Similar to the LogProcessor and TCDataWSProcessor, you could abstract WSCommModule with a communication 
    interface. This would allow UIRequestProcessor to interact with other communication methods, such as HTTP,
    if needed in the future.
    - This would also let you centralize WebSocket handling in MessageBroadcaster, aligning with the overall 
    decoupling strategy you've been developing. 

2. Implement a Response Handling Strategy
    - To address the need for handling one interaction at a time, consider a state or semaphore-based approach to 
    queue UI requests:
        - Semaphore: You could use a semaphore that limits UIRequestsProcessor to one active interaction until 
        the response is received.
        - Interaction Queue: For more complex interaction handling, an internal queue could buffer incoming requests.
        The processor could handle one request at a time and wait for a response, only moving to the next interaction
        once the previous one is completed.

3. Centralize Interaction Handling Logic in MessageBroadcaster:
    - UIRequestProcessor could use MessageBroadcaster instead of sending WebSocket messages directly. Adding a method 
    like broadcast_ui_prompt in MessageBroadcaster would allow UIRequestProcessor to focus on managing InteractionContext
    objects while MEssageBroadcaster handles all communication logic.

4. Response Processing Strategy:
    - For processing responses, you could have a response_channel that receives responses from the UI. After sending a prompt, 
    UIRequestProcessor would wait for a response on this channel before processing the next interaction.
    - Alternatively, InteractionContext could hold its own state for responses. For example, it could manage a "response_received"
    flag and a callback method to handle the response when it arrives, making it easier  to keep track of response states.
"""
