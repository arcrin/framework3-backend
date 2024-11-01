from _CommunicationModules._WSCommModule import WSCommModule
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
The UIRequestProcessor class is designed to process user interface requests by forwarding them to
a WebSocket connection managed by WSCommModule. This setup is well-structured for handling real-time
interactions with users, but there are areas where you can improve robustness and functionality.

    1. Error Handling and Connection Management
        - Graceful Connection Handling: Currently, if the WebSocket connection is closed, the process
        raises an exception and stops. Consider reconnecting or implementing a retry mechanism to
        handle temporary network issues or server restarts gracefully.

        - Error Handling Improvements: Improve error handling by distinguishing between different types
        of exceptions. For instance, handle serialization errors separately from communication errors, 
        allowing for more specific recovery actions. 

    2. Managing User Interaction States
        - Handling Single Interactions: If you need to process one interaction at a time, consider 
        implementing a semaphore or another locking mechanism to control the processing flow. This
        can be useful if interactions must be processed in a sequence or if they depend on previous
        interactions' responses.

        - Response Handling: Since you commented on the need for a waiting mechanism without directly
        interacting with another channel, consider how you might structure this with trio's synchronization 
        primitives or by using an event or condition variable that can be awaited until the necessary 
        condition (response ready) is met.

    3. Testing and Reliability
        - Testing: Develop thorough tests that simulate various scenarios, including lost connections,
        malformed messages, and server-side failures. Ensure that your system handles these gracefully.

        - Message Formatting and Validation: Make sure that the messages sent to the WebSocket are
        correctly formatted and validated before sending. This avoids sending potentially malformed
        data that could lead to errors on the client side.

    4. Logging and Monitoring
        - Detailed Logging: Extend logging to include not just errors but also debug information about
        the messages being sent and their content (if not sensitive). This can help in debugging issues
        in production.
"""
