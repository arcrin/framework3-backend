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
from _Node._BaseNode import BaseNode
from _Node._TCNode import TCNode
from typing import TYPE_CHECKING, Dict, Any, Callable, Type, Tuple, List, Coroutine, TypeVar 
import json
import trio
import logging

if TYPE_CHECKING:
    from trio import MemorySendChannel
    from trio_websocket import WebSocketConnection  # type: ignore

E = TypeVar("E", bound=BaseEvent)

class ApplicationStateManager():
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
        self._tc_data_send_channel = tc_data_send_channel
        self._node_executor_send_channel = node_executor_send_channel
        self._ui_request_send_channel = ui_request_send_channel
        self._test_profile = test_profile  # type: ignore
        self._control_session: ControlSession | None = None
        self._sessions: Dict["WebSocketConnection", Session] = {}
        self._interactions: Dict[str, InteractionContext] = {}
        self._logger = logging.getLogger("ApplicationStateManager")

        event_register: List[Tuple[Type[BaseEvent], Callable[[BaseEvent], Coroutine[Any, Any, None]]]]= [ 
            # type: ignore . Static type check has trouble recognize the sub clsss events
            (NewTestCaseEvent, self.handle_new_test_case_event),        
            (ParameterUpdateEvent, self.handle_parameter_update_event),
            (ProgressUpdateEvent, self.handle_progress_update_event),
            (NewTestExecutionEvent, self.handle_new_test_execution_event),
            (TestRunTerminationEvent, self.handle_test_run_termination_event),
            (TestCaseFailEvent, self.handle_test_case_fail_event),
            (UserInteractionEvent, self.handle_user_interaction_event),
            (NodeReadyEvent, self.handle_node_ready_event),
            (UserResponseEvent, self.handle_user_response_event),
            (NewViewSessionEvent, self.handle_new_session_event),
        ]
        
        for event_type, handler in event_register:
            SystemEventBus.subscribe_to_event(event_type, handler) 


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
            await SystemEventBus.publish(new_view_session_event)
        self._sessions[ws_connection] = new_session

    def remove_session(self, ws_connection: "WebSocketConnection"):
        session = self._sessions.pop(ws_connection)
        if isinstance(session, ControlSession):
            self._control_session = None

    async def handle_new_test_case_event(self, event: NewTestCaseEvent):
        if isinstance( event.payload, TCNode):  # FIXME: Is this necessary for type checking?
            self._logger.info( f"New test case added to test run {event.payload.name} ")
            tc_node = event.payload
            react_ui_data_payload = { # type: ignore
                "type": "tc_data",
                "event_type": "newTC",
                "payload": tc_node.data_model.react_ui_payload,
            }
            async with trio.open_nursery() as nursery:
                nursery.start_soon(self._tc_data_send_channel.send, react_ui_data_payload) # type: ignore
        else:
            self._logger.error("New test case event payload is not of type TCNode")
            raise (TypeError("New test case event payload is not of type TCNode"))
        
    async def handle_parameter_update_event(self, event: ParameterUpdateEvent):
        self._logger.info( f"Parameter updated for test case {event.payload['tc_id']}")
        async with trio.open_nursery() as nursery:
            nursery.start_soon( # type: ignore
                self._tc_data_send_channel.send,
                {
                    "type": "tc_data",
                    "event_type": "parameterUpdate",
                    "payload": event.payload,
                },
            )
            
    async def handle_progress_update_event(self, event: ProgressUpdateEvent):
        tc_data_model = event.payload
        if isinstance(tc_data_model, TestCaseDataModel):
            self._logger.info(f"Progress updated for test case {tc_data_model.id}")
            react_ui_data_payload = { # type: ignore
                "type": "tc_data",
                "event_type": "progressUpdate",
                "payload": {
                    "tc_id": tc_data_model.id,
                    "progress": tc_data_model.progress,
                },
            }
            async with trio.open_nursery() as nursery:
                nursery.start_soon(self._tc_data_send_channel.send, react_ui_data_payload) # type: ignore
        else:
            self._logger.error("Progress update event payload is not of type TestCaseDataModel")
            raise ( TypeError( "Progress update event payload is not of type TestCaseDataModel"))
        
    async def handle_new_test_execution_event(self, event: NewTestExecutionEvent):
        self._logger.info( f"New execution added to test case {event.payload['tc_id']}")
        async with trio.open_nursery() as nursery:
            nursery.start_soon( # type: ignore
                self._tc_data_send_channel.send,
                {
                    "type": "tc_data",
                    "event_type": "newExecution",
                    "payload": event.payload,
                },
            )
            
    async def handle_test_run_termination_event(self, event: TestRunTerminationEvent):
        self._logger.info(f"Test run {event.payload['tr_id']} terminated")
        async with trio.open_nursery() as nursery:
            nursery.start_soon(
                self._tc_data_send_channel.send,
                {
                    "type": "tc_data",
                    "event_type": "testRunTermination",
                },
            )

    async def handle_test_case_fail_event(self, event: TestCaseFailEvent):
        self._logger.info(f"Test case {event.payload['tc_id']} failed")
        async with trio.open_nursery() as nursery:
            nursery.start_soon( # type: ignore
                self._tc_data_send_channel.send,
                {
                    "type": "tc_data",
                    "event_type": "testCaseFail",
                    "payload": event.payload,
                },
            )
            
    async def handle_user_interaction_event(self, event: UserInteractionEvent):
        if isinstance(event.payload, InteractionContext):
            self._logger.info(f"User interaction id {event.payload.id}")
            self._interactions[event.payload.id] = event.payload
            async with trio.open_nursery() as nursery:
                nursery.start_soon(  # type: ignore
                    self._ui_request_send_channel.send,
                    event.payload,
                )
        else:
            raise TypeError( "User interaction event payload is not of type InteractionContext")
        
    async def handle_node_ready_event(self, event: NodeReadyEvent):
        if isinstance(event.payload, BaseNode):
            self._logger.info(f"Node {event.payload.id} ready")
            async with trio.open_nursery() as nursery:
                nursery.start_soon(
                    self._node_executor_send_channel.send, event.payload
                )
        else:
            raise TypeError("Node ready event payload is not of type BaseNode")
        
    async def handle_user_response_event(self, event: UserResponseEvent):
        self._interactions[event.payload['id']].response = event.payload['response']
        del self._interactions[event.payload['id']]
        self._logger.info(f"User response received for interaction {event.payload['id']}")

    async def handle_new_session_event(self, event: NewViewSessionEvent):
        if isinstance(event.payload, ViewSession):
            connection = event.payload.connection
            if self.control_session:
                async with trio.open_nursery() as nursery:
                    for panel in self.control_session.panels:
                        for tc_node in panel.tc_nodes:
                            react_ui_data_payload = { # type: ignore
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

# COMMENT
"""
ApplicationStateManager class is a central hub managing different aspects of application state,
handling various events, and interfacing with other parts of the system. it orchestrates interactions,
session management, and communication across various components.

Key Roles:

    - Event Handling: The class subscribes to and event bus and handles a variety of events, each with 
    specific actions related to the state of the application or UI updates. This design pattern helps
    decouple the state management from the event generation and handling logic.

    - Session Management: Manages both control and view sessions, indicating a multi-use or multi-view
    capability within the application. This is crucial for systems where simultaneous access and interaction 
    are required.

    - Interaction with Trio: Utilizes Trio's asynchronous capabilities effectively to manage non-blocking
    communication and task execution, which is appropriate for handling I/O or network-related operations
    within event handlers.
    
Refactoring:
    
    - Centralized Error Handling: Consider centralizing your error handling logic, perhaps by using 
    a decorator or a bse class method to wrap event handling methods. This can reduce code
    duplication and make maintenance easier.

    - Optimize Event Handling: Depending on the frequence and complexity of events, consider
    implementing more sophisticated handling strategies such as throttling or debouncing,
    especially useful in systems with high frequence updates.

    - Testing: Ensure that each part of your event handling is thoroughly tested, particularly given
    the asynchronous nature of the operations. trio provides tools for testing asynchronous 
    code which you should leverage to ensure your handlers work as expected under various
    conditions.

    - Documentation:

    - Resource Management: In your asynchronous blocks, particularly where you're opening
    nurseries, ensure that resources are managed properly to avoid leaks or unintended side 
    effects. Trio handles many aspects of asynchronous resource management, but it's good 
    practice to review these to ensure they align with your application's needs.
    """