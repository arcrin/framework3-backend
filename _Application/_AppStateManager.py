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

"""
The ApplicationStateManager class plays a crucial role in the system by acting as the central point for managing application states,
handling various events, and bridging components like the event bus, sessions, and channels.

Strengths of the Current Implementation
1. Centralized Event Handling:
    - All event types and their handlers are registered and managed in one place, ensuring that the system remains coherent and organized.
    - The event_register list provides a clean way to map events to their corresponding handlers.

2. Seamless Integration with the Event Bus:
    - The SystemEventBus is leveraged effectively, decoupling event producers and consumers while ensuring that state changes and actions
    are processed asynchronously.

3. Clear State Management:
    - The use of _control_session, _sessions, and _interactions ensures that the application state is well-organized.
    - Each session type is managed explicitly, and interactions are tracked in a dictionary for quick access.

4. Asynchronous Processing:
    - Handlers use trio.open_nursery() to allow concurrent execution, preventing blocking while processing events.

5. User Interaction Handling;
    - The use of InteractionContext for managing user inputs and responses demonstrates a thoughtful design for interactive workflows.

6. Session Awareness:
    - The add_session and remove_session methods ensure that sessions are added or removed cleanly and appropriately notify the system
    of their state.

Areas for Improvement
1. Event Processing Resilience
    - If an exception occurs in one event handler, it could disrupt the handling of other events in the same nursery.

    Solution:
        - Wrap individual handler calls in try-except blocks to isolate errors:

            async def handle_event_safe(handler, event):
                try:
                    await handler(event)
                except Exception as e:
                    self._logger.error(f"Error processing event {type(event).__name__}: {e}")

            async def handle_new_test_case_event(self, event: NewTestCaseEvent):
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(handle_event_safe, self._tc_data_send_channel.send, ...)
                    
2. Avoid Blocking on a Single Stuck Event
    - A TODO in your code notes the risk of an event blocking other events. If one handler hangs, other events might not be processed.

    Solution:
        - Use timeouts or separate channels for event handlers.
        Example:

            async def handle_event_with_timeout(handler, event, timeout=5):
                try:
                    with trio.fail_after(timeout):
                        await handler(event)
                except trio.ToolSlowError:
                    self._logger.warning(f"Event {type(event).__name__} handling timed out.")


3. Modularize Event Handlers
    - As the number of event types grows, the ApplicationStateManger class might become bloated.

    Solution:
        - Move event handler logic to separate helper classes or modules. For example, create a SessionHandler, TestCaseHandler, etc.,
        and delegate handling to them.

4. Validation of Event Payloads
    - Many handlers check the payload type using isinstance and raise exceptions. This could be streamlined to reduce boilerplate.

    Solution:
        - Use a utility method for validation:

            def validate_payload(event: BaseEvent, expected_type: Type):
                if not isinstance(event.payload, expected_type):
                    raise TypeError(f"Expected payload of type {expected_type}, got {type()})
                    
        - Example usage:

            async def handle_new_test_case_event(self, event: NewTestCaseEvent):
                validate_payload(event, TCNode)
                ...

5. Refactor event_register
    - The event_register list is a great concept, but it could be more dynamic or declarative

    Solution:
        - Use a decorator-based approach for cleaner registration:

            event_handlers = {}

            def event_handler(event_type: Type[BaseEvent]):
                def decorator(func):
                    event_handlers[event_type] = func
                    return func
                return decorator

            @event_handler(NewTestCaseEvent)
            async def handle_new_test_case_event(self, event: NewTestCaseEvent):

        - Register all handlers dynamically

            for event_type, handler in event_handlers.items():
                SystemEventBus.subscribe_to_event(event_type, handler)

6. Testing and Debugging
    - Logging is already well-integrated, but you could enhance it for debugging:
        - Add a method to inspect the current state of _control_session, _sessions, and _interactions.
        - Track the number of pending events and processed events for monitoring.


Questions to Consider
1. Scalability:
    - How many event types do you anticipate? Will ApplicationStateManager become too complex to maintain as new handlers are added?

2. Concurrency:
    - Are there scenarios where two events might conflict (e.g., modifying _control_session)? if so, should locks or stricter synchronization
    be added?

3. Testing:
    - Have you considered unit tests for individual event handlers? Mocking the event bus and testing each handler in isolation would ensure
    reliability.


Final Thoughts

The ApplicationStateManager is a well-thought-out central hub for managing application state and events. It works well for the current
scope but may benefit from modularization and additional error handling as it grows.
"""