from _Application._SystemEvent import (
    NewTestCaseEvent,
    ParameterUpdateEvent,
    ProgressUpdateEvent,
    NewTestExecutionEvent,
    TestRunTerminationEvent,
    TestCaseFailEvent,
    UserInteractionEvent,
    NodeReadyEvent,
    UserResponseEvent,
    NewViewSessionEvent
)
from _Application._DomainEntity._Session import Session, ControlSession, ViewSession
from _Application._SystemEventBus import SystemEventBus
from _Application._SystemEvent import BaseEvent
from _Application._DomainEntity._TestCaseDataModel import TestCaseDataModel
from util._InteractionContext import InteractionContext
from _Application._DomainEntity._Session import ViewSession
from _Node._BaseNode import BaseNode
from _Node._TCNode import TCNode
from typing import TYPE_CHECKING, Dict, Any
import json
import trio
import logging

if TYPE_CHECKING:
    from trio import MemorySendChannel
    from trio_websocket import WebSocketConnection  # type: ignore


class ApplicationStateManager:
    def __init__(
        self,
        tc_data_send_channel: "MemorySendChannel[Dict[Any, Any]]",
        node_executor_send_channel: "MemorySendChannel[BaseNode]",
        ui_request_send_channel: "MemorySendChannel[InteractionContext]",
        test_profile,  # type: ignore
    ):
        self._app_state = {}
        self._control_context = {}
        self._app_data = {}
        self._event_bus = SystemEventBus()
        self._event_bus.subscribe(self.event_handler)
        self._tc_data_send_channel = tc_data_send_channel
        self._node_executor_send_channel = node_executor_send_channel
        self._ui_request_send_channel = ui_request_send_channel
        self._test_profile = test_profile  # type: ignore
        self._control_session: ControlSession | None = None
        self._sessions: Dict["WebSocketConnection", Session] = {}
        self._interactions: Dict[str, InteractionContext] = {}
        self._logger = logging.getLogger("ApplicationStateManager")

    @property
    def control_session(self):
        return self._control_session

    @property
    def sessions(self):
        return self._sessions

    async def add_session(self, ws_connection: "WebSocketConnection"):
        if not self._control_session:
            new_session = ControlSession(
                ws_connection,
                self._test_profile,  # type: ignore
            )
            self._control_session = new_session
        else:
            new_session = ViewSession(ws_connection)
            new_view_session_event = NewViewSessionEvent(new_session)   
            await self._event_bus.publish(new_view_session_event)
        self._sessions[ws_connection] = new_session

    def remove_session(self, ws_connection: "WebSocketConnection"):
        session = self._sessions.pop(ws_connection)
        if isinstance(session, ControlSession):
            self._control_session = None

    async def event_handler(self, event: BaseEvent):
        if isinstance(event, NewTestCaseEvent):
            if isinstance(
                event.payload, TCNode
            ):  # FIXME: Is this necessary for type checking?
                self._logger.info(
                    f"New test case added to test run {event.payload.name} "
                )
                tc_node = event.payload
                react_ui_data_payload = {
                    "type": "tc_data",
                    "event_type": "newTC",
                    "payload": tc_node.data_model.react_ui_payload,
                }
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(
                        self._tc_data_send_channel.send, react_ui_data_payload
                    )
            else:
                self._logger.error("New test case event payload is not of type TCNode")
                raise (TypeError("New test case event payload is not of type TCNode"))
        elif isinstance(event, ParameterUpdateEvent):
            self._logger.info(
                f"Parameter updated for test case {event.payload['tc_id']}"
            )
            async with trio.open_nursery() as nursery:
                nursery.start_soon(
                    self._tc_data_send_channel.send,
                    {
                        "type": "tc_data",
                        "event_type": "parameterUpdate",
                        "payload": event.payload,
                    },
                )

        elif isinstance(event, ProgressUpdateEvent):
            tc_data_model = event.payload
            if isinstance(tc_data_model, TestCaseDataModel):
                self._logger.info(f"Progress updated for test case {tc_data_model.id}")
                react_ui_data_payload = {
                    "type": "tc_data",
                    "event_type": "progressUpdate",
                    "payload": {
                        "tc_id": tc_data_model.id,
                        "progress": tc_data_model.progress,
                    },
                }
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(
                        self._tc_data_send_channel.send, react_ui_data_payload
                    )
            else:
                self._logger.error(
                    "Progress update event payload is not of type TestCaseDataModel"
                )
                raise (
                    TypeError(
                        "Progress update event payload is not of type TestCaseDataModel"
                    )
                )
        elif isinstance(event, NewTestExecutionEvent):
            self._logger.info(
                f"New execution added to test case {event.payload['tc_id']}"
            )
            async with trio.open_nursery() as nursery:
                nursery.start_soon(
                    self._tc_data_send_channel.send,
                    {
                        "type": "tc_data",
                        "event_type": "newExecution",
                        "payload": event.payload,
                    },
                )

        elif isinstance(event, TestRunTerminationEvent):
            self._logger.info(f"Test run {event.payload['tr_id']} terminated")
            async with trio.open_nursery() as nursery:
                nursery.start_soon(
                    self._tc_data_send_channel.send,
                    {
                        "type": "tc_data",
                        "event_type": "testRunTermination",
                    },
                )
        elif isinstance(event, TestCaseFailEvent):
            self._logger.info(f"Test case {event.payload['tc_id']} failed")
            async with trio.open_nursery() as nursery:
                nursery.start_soon(
                    self._tc_data_send_channel.send,
                    {
                        "type": "tc_data",
                        "event_type": "testCaseFail",
                        "payload": event.payload,
                    },
                )

        elif isinstance(event, UserInteractionEvent):
            if isinstance(event.payload, InteractionContext):
                self._logger.info(f"User interaction id {event.payload.id}")
                self._interactions[event.payload.id] = event.payload
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(  # type: ignore
                        self._ui_request_send_channel.send,
                        event.payload,
                    )
            else:
                raise TypeError(
                    "User interaction event payload is not of type InteractionContext"
                )

        elif isinstance(event, NodeReadyEvent):
            if isinstance(event.payload, BaseNode):
                self._logger.info(f"Node {event.payload.id} ready")
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(
                        self._node_executor_send_channel.send, event.payload
                    )
            else:
                raise TypeError("Node ready event payload is not of type BaseNode")
            
        elif isinstance(event, UserResponseEvent):
            self._interactions[event.payload['id']].response = event.payload['response']
            del self._interactions[event.payload['id']]
            self._logger.info(f"User response received for interaction {event.payload['id']}")

        elif isinstance(event, NewViewSessionEvent):
            if isinstance(event.payload, ViewSession):
                connection = event.payload.connection
                if self.control_session:
                    async with trio.open_nursery() as nursery:
                        for panel in self.control_session.panels:
                            for tc_node in panel.tc_nodes:
                                react_ui_data_payload = {
                                    "type": "tc_data",
                                    "event_type": "newTC",
                                    "payload": tc_node.data_model.react_ui_payload,
                                }
                                nursery.start_soon(connection.send_message, json.dumps(react_ui_data_payload)) # type: ignore
                else:
                    self._logger.error("No control session is associated with the current application")
                    raise ValueError("No control session is associated with the current application")
                self._logger.info(f"New view session {event.payload.id} added ")
            else:
                raise TypeError("New view session event payload is not of type WebSocketConnection")    

# TODO: I should confirm that other event can be processed with some other event is stuck