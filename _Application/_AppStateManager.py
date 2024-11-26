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


Why Modularize Event Handlers?
1. Improved Readability:
    - Separating event handlers into distinct modules makes it easier to locate, understand, and maintain them.

2. Focused Responsibilities:
    - Each handler module can focus on a specific domain or functionality (e.g., session management, test case updates).

3. Reusability:
    - Decoupled handlers can be reused in other parts of the system if needed

4. Scalability:
    - As the number of event types grows, modularization prevents a monolithic ApplicationStateManager class.

Approaches to Modularizing Handlers
1. Group by Functionality
Create separate handler classes for each logical domain of the application. For example:
    - SessionHandlers: Handles events related to sessions (e.g., NewViewSessionEvent).
    - TestCaseHandlers: Handles events related to test cases (e.g., NewTestEvent, ProgressUpdateEvent).
    - NodeHandlers: Handles events related to nodes (e.g., NodeReadyEvent).
    
    Example Folder Structure:
    
        application/
            handlers/
                __init__.py
                session_handler.py
                test_case_handler.py
                node_handler.py

    Implementation:
    - session_handler.py
        
        class SessionHandler:
            def __init__(self, app_state_manager):
                self._app_state_manager = app_state_manager

            async def handle_new_view_session(self, event):
                # Logic for handling NewViewSessionsEvent

    - Register the handlers:

        from application.handlers.session_handler import SessionHandler
        from application.handlers.test_case_handler import TestCaseHandler

        class ApplicationStateManager:
            def __init__(...):
                self._session_handler = SessionHandler(self)
                self._test_case_handler = TestCaseHandler(self)
                
                event_register = [
                    (NewViewSessionEvent, self._session_handler.handle_new_view_session),
                    (NewTestCaseEvent, self._test_case_handler.handle_new_test_case),
                    ...
                ]
                for event_type, handler in event_register:
                    SystemEventBus.subscribe_to_event(event_type, handler)

2. Group by Event Types
If you want a more event-centric grouping, create a separate file or class for each event type. Each handler would 
process a single event.

    Example Folder Structure:
        application/
            event_handlers/
                __init__.py
                new_test_case_event_handler.py
                progress_update_event_handler.py
                user_interaction_event_handler.py

    Implementation:
    - new_test_case_event_handler.py

        class NewTestCaseEventHandler:
            async def handle(self, event):
                # Logic for NewTestCaseEvent
                ...

    Register the handlers:

        from application.event_handlers.new_test_case_event_handler import NewTestCaseEventHandler

        class ApplicationStateManager:
            def __init__(...):
                self._new_test_case_event_handler = NewTestCaseEventHandler()

                event_register = [
                    (NewTestCaseEvent, self._new_test_case_event_handler.handle),
                    ...
                ]
                for event_type, handler in event_register:
                    SystemEventBus.subscribe_to_event(event_type, handler)

3. Combine with Dependency Injection
Instead of the ApplicationStateManager passing itself to handlers, use a Dependency Injection (DI) container to supply dependencies.
This makes testing and reusing handlers easier.

Implementation:
    - Use a DI library like injector or a custom DI pattern:

        from injector import inject

        class SessionHandler:
            @inject
            def __init__(self, session_service, logging_service)
                self._session_service = session_service
                self._logger = logging_service

            async def handle_new_view_session(self, event):
                # Logic for handling session events
                ...

    - Define a DI container to wire dependencies and register handlers.


4. Dynamic Handler Discovery
Use Python's importlib or similar libraries to dynamically discover and register handlers. This approach is useful for plugin-based
architectures or systems with a large number of handlers.

Implementation:
    - Organize handlers into a specific folder
    - Use importlib to load them dynamically:

        import importlib
        import os

        def load_handlers(folder):
            for file in os.listdir(folder):
                if file.endswith("_handler.py"):
                    module = importlib.import_module(f"{folder}.{file[:-3]}")
                    yield module

    - Dynamically register handlers:

        for handler_module in load_handlers("application.event_handlers"):
            for event_type, handler in handler_module.get_handlers():
                SystemEventBus.subscribe_to_event(event_type, handler)


Pros
    - Readability: Clear separation of concerns.
    - Testability: Handlers are easier to test in isolation
    - Maintainability: Adding or modifying a handler doesn't require changes to the monolithic ApplicationStateManager.
    - Scalability: Better suited for large or grouwing systems.

Cons
    - Increased Boilerplate: Requires more files and classes.
    - Overhead for Small Systems: For small projects, the added complexity may not be worth it.

Choosing the Right Approach
1. Small Systems:
    - Stick with your current structure or group handlers by functionality (Option 1).

2. Medium Systems:
    - Use a combination of Option 1 and Option 2 for better clarity.

3. Large or Plugin-Based Systems:
    - Consider DI or dynamic discovery (Options 3 and 4)
    

    
Modularizing event handlers using Dependency Injection (DI) enhances flexibility, testability, and scalability by decoupling
the handlers form their dependencies. DI ensures that each handler receives the components it needs without directly constructing
or importing them. This approach aligns well with modular architecture and clean code principles.

What is Dependency Injection (DI)?
    - Definition: DI is a design pattern where dependencies are provided to a class or function rather than being created or fetched
    within it.
    - How it works: A DI container manages object creation and wiring, ensuring dependencies are injected at runtime.

Steps to Modularize Handlers with DI
1. Define handlers as Separate Classes
Each handler is a class with a single responsibility - handling a specific type of event or related events. Dependencies required by
the handler are passed via its constructor. 

    Example:
        
        form _Application._SystemEvent import NewTestCaseEvent
        from typing import TYPE_CHECKING
        import logging

        if TYPE_CHECKING:
            from _Application._DomainEntity._TestCaseDataModel import TestCaseDataModel
            from trio import MemorySendChannel

        
        class testCaseHandler:
            def __init__(self, tc_data_send_channel: "MemorySendChannel"):
                self._tc_data_send_channel = tc_data_send_channel
                self._logger = logging.getLogger("TesCaseHandler")

            async def handler_new_test_case(self, event: NewTestCaseEvent):
                self._logger.info(f"Handling new test case: {event.payload.name}")
                react_ui_data_payload = {
                    "type": "tc_data",
                    "event_type": "newTC",
                    "payload": event.payload.data_model.react_ui_payload,
                }
                await self._tc_data_send_channel.send(react_ui_data_payload)
                
2. Use a DI Container
A DI container is responsible for managing the lifecycle of objects and injecting dependencies. Libraries like injector make this process straightforward.

    Example with injector:

        from injector import Injector, inject, singleton

        # Define DI container modules
        class ApplicationModule:
            @singleton
            @inject
            def provide_tc_data_send_channel(self) -> "MemorySendChannel":
                # Create and return the channel (placeholder for actual implementation)
                return MemorySendChannel()

            @singleton
            @inject
            def provide_test_case_handler(self, tc_data_send_channel: "MemorySendChannel") -> TestCaseHandler:
                return TestCaseHandler(tc_data_send_channel)

        injector = Injector([ApplicationModule])

3. Register Handlers Dynamically
Use the DI container to resolve and register handlers with the SystemEventBus.

    Example:

        class ApplicationStateManager:
            def __init__(self, injector: Injector):
                self._logger = logging.getLogger("ApplicationStateManager")

                # Resolve handlers
                test_case_handler = injector.get(TestCaseHandler)

                # Register handlers with the SystemEventBus
                event_register = [
                    (NewTestCaseEvent, test_case_handler.handle_new_test_case),
                    # Add other event-handler pairs here
                ]

                for event_type, handler in event_register:
                    SystemEventBus.subscribe_to_event(event_type, handler)

4. Testing with Mocks
DI makes testing straightforward by allowing you to replace real dependencies with mocks during tests.

    Example:

        from unittest.mock import AsyncMock, MagicMock

        def test_test_case_handler():
            # Mock the dependencies
            mock_send_channel = AsyncMock()

            # Crate the handler
            handler = TestCaseHandler(mock_send_channel)

            # Create a mock event
            mock_event = MagicMock()
            mock_event.payload.name = "TestCase"
            mock_event.payload.data_model.react_ui_payload = {"id": 1, "name": "TestCase1"}

            # Run the handler
            trio.run(handler.handle_new_test_case, mock_event)

            # Asser that the channel send method was called with the correct payload
            mock_send_channel.send_assert_called_once_with({
                "type": "tc_data",
                "event_type": "newTC",
                "payload": {"id": 1, "name": "Testcase1"},
            })

Advantages of DI for Modularizing Handlers
1. Improved Testability:
    - Handlers are decoupled fro their dependencies, making it easy to inject mocks for unit testing

2. Easier Refactoring:
    - Changes to a handler's dependencies don't require changes to the handler itself, as long as the interface remains consistent.

3. Centralized Dependency Management:
    - Dependencies are declared in one place (DI container), making it easy to understand and modify the application's architecture.

4. Reusability:
    - Handlers and their dependencies can be reused across different contexts or applications.

5. Reduced Boilerplate in Handlers:
    - Handlers dont't need to instantiate or manage their dependencies, keeping them focused on their core logic.
    

When to use DI for Event Handlers
- Complex Systems: When there are many handlers and dependencies.
- Test-Driven Development: If you aim for high test coverage and clean separation of concerns.
- Dynamic Environments: Where dependencies or implementations might change (e.g., switching a message queue system).


Challenges with DI
1. Learning Curve:
    - For teams new to DI, understanding and implementing it might take some time.

2. Overhead for Small Projects:
    - In simple systems, manually managing dependencies might be more straightforward than setting up DI.

3. Debugging:
    - Indirect wiring of dependencies via DI can make it harder to trace issues during debugging.

Conclusion
DI adds structure and flexibility to your system. While it might seem like an overhead for smaller systems, it pays off as your application grows in complexity.

"""