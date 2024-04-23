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
