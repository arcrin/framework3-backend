from typing import List, TYPE_CHECKING, cast, Dict, Any
from util._InteractionContext import InteractionContext, InteractionType
from _Application._DomainEntity._Parameter import Parameter
from _Application._SystemEventBus import SystemEventBus
from _Application._SystemEvent import (
    ParameterUpdateEvent,
    ProgressUpdateEvent,
    NewTestExecutionEvent,
    UserInteractionEvent
)
from datetime import datetime

if TYPE_CHECKING:
    from _Application._DomainEntity._TestRun import TestRun
    from _Node._BaseNode import NodeState


class TestExecution:
    def __init__(
        self,
        execution_id: int,
    ):
        self._execution_id: int = execution_id
        self._timestamp: datetime = datetime.now()
        self._test_duration: float = 0.0
        self._parameters: List[Parameter] = []
        self._progress: int = 0

    @property
    def execution_id(self) -> int:
        return self._execution_id

    @execution_id.setter
    def execution_id(self, value: int):
        self._execution_id = value

    @property
    def progress(self) -> int:
        return self._progress

    @progress.setter
    def progress(self, value: int):
        self._progress = value

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def test_duration(self) -> float:
        return self._test_duration

    @test_duration.setter
    def test_duration(self, value: float):
        self._test_duration = value

    @property
    def parameters(self) -> List[Parameter]:
        return self._parameters
    
    @property
    def react_ui_parameter_data(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for parameter in self._parameters:
            data[parameter.name] = parameter.as_dict()
        return data

    @timestamp.setter
    def timestamp(self, value: datetime):
        self._timestamp = value

    def update_parameter(self, parameter: Parameter):
        self._parameters.append(parameter)


class TestCaseDataModel:
    def __init__(
        self,
        tc_id: str,
        test_case_name: str,
        test_description: str,
    ):
        self._test_case_name: str = test_case_name
        self._test_description: str = test_description
        self._tc_id: str = tc_id
        self._execution: List[TestExecution] = []
        self._parent_test_run: "TestRun" = cast("TestRun", None)
        self._state: "NodeState"

    @property
    def name(self) -> str:
        return self._test_case_name

    @property
    def id(self) -> str:
        return self._tc_id

    @property
    def parent_tr_id(self) -> str:
        return self._parent_test_run.id

    @property
    def parent_panel_id(self) -> int:
        return self._parent_test_run.parent_panel_id

    @property
    def parent_session_id(self) -> str:
        return self._parent_test_run.parent_control_session_id

    @property
    def state(self) -> "NodeState":
        return self._state

    @property
    def progress(self) -> int:
        try:
            return self.current_execution.progress
        except IndexError:
            return 0

    @state.setter
    def state(self, value: "NodeState"):
        self._state = value
    
    @property
    def parent_test_run(self) -> "TestRun | None":
        return self._parent_test_run

    @parent_test_run.setter
    def parent_test_run(self, value: "TestRun"):
        if not self._parent_test_run:
            self._parent_test_run = value

    @property
    def current_execution(self) -> TestExecution:
        return self._execution[-1]

    @property
    def react_ui_payload(self) -> Dict[str, Any]:
        execution_data = {}
        for execution in self._execution:
            execution_data[execution.execution_id] = {
                "id": execution.execution_id,
                "name": f"Execution {execution.execution_id + 1}",
                "parameters": execution.react_ui_parameter_data,
            }
        payload: Dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "tr_id": self.parent_tr_id,
            "panel_id": self.parent_panel_id,
            "session_id": self.parent_session_id,
            "progress": self.progress,
            "tc_state": self.state.value,
            "executions": execution_data,
        }
        return payload

    async def add_execution(self):
        execution = TestExecution(len(self._execution))
        self._execution.append(execution)
        new_test_execution_event = NewTestExecutionEvent(
            {
                "tc_id": self.id,
                "execution_id": execution.execution_id,
                "tc_state": self.state.value,
            }
        )
        await SystemEventBus.publish(new_test_execution_event)

    async def update_parameter(self, parameter: Parameter):
        assert len(self._execution) > 0, "No execution to update parameter"
        self.current_execution.update_parameter(parameter)

        parameter_update_event = ParameterUpdateEvent(
            {
                "tc_id": self.id,
                "execution_id": self.current_execution.execution_id,
                "parameter": {parameter.name: parameter.as_dict()},
            }  # type: ignore
        )
        await SystemEventBus.publish(parameter_update_event)

    async def update_progress(self, progress: int):
        self._execution[-1].progress = progress
        progress_update_event = ProgressUpdateEvent(self)
        await SystemEventBus.publish(progress_update_event)

    async def user_input_request(self, message: str) -> str:
        # TODO: handle multiple user interactions at test case level
        interaction_context = InteractionContext(InteractionType.InputRequest, message)
        user_interaction_event = UserInteractionEvent(interaction_context)
        await SystemEventBus.publish(user_interaction_event)
        await interaction_context.response_ready()
        return interaction_context.response # type: ignore



"""
Key Responsibilities of TestCaseDataModel
1. Execution Tracking:
    - Maintains a list of TestExecution Objects for each test case, tracking parameters, progress, and results.
    - Provides methods to add new executions and update parameters or progress for the current execution.

2. Parent and Hierarchical References:
    - Stores a reference to its parent TestRun, and indirectly accesses parent panel and session IDs through parent_test_run.
    - Exposes hierarchical context (e.g., parent_tr_id, parent_panel_id, parent_session_id) for reporting and UI payload generation.

3. Event-Driven Design:
    - Publishes events to the SystemEventBus for key updates like new executions, parameter changes, progress updates, and user interactions.

4. UI Data Representation:
    - Generates structured payloads (react_ui_payload) for consumption by the user interface.

Strengths
1. Well-Defined Execution Tracking:
    - The use of TestExecution to encapsulate individual execution details provides a clear separation of concerns and makes it easier to 
    manage and query execution history.

2. Event-Driven notifications:
    - Publishing events ensures that updates are decoupled from direct references to other components, improving flexibility and testability.

3. User Interaction Handling:
    - Encapsulation of user input requests within TestCaseDataModel is intuitive and aligns well with test case-level operations.

4. UI Integration:
    - Methods like react_ui_payload and react_ui_parameter_data make it straightforward to generate data for the frontend.
    

Areas for Improvement
1. Remove Parent References (parent_test_run):
    - To maintain a strict hierarchical model, avoid bidirectional relationships between TestCaseDataMOdel and TestRun.
    - Replace these references with @property accessors or event-based communication.
    Example:
        - Instead of parent_test_run, let TestRun manage the relationship and query TestCaseDataModel state when needed.

2. Simplify Hierarchical Context:
    - The properties parent_tr_id, and parent_session_id are derived from the hierarchy and could be redundant.
    - Remove these and let the higher-level components (like TestRun or Panel) handle context-specific operations.

3. Centralize UI PayLoads:
    - Generating react_ui_payload within TestCaseDataModel tightly couples the model with the UI structure.
    - Consider moving payload generation to a dedicated service or serializer to keep the data model focused on business logic.

4. Error Handling for Empty Executions:
    - Properties like current_execution and methods like update_parameter assume that there's always an active execution, which may not 
    always be the case.
    - Add error handling or defaults for scenarios where no executions exist.

    
Event Bus Usage

Pros
1. Decoupling
    - The TestCaseDataModel doesn't need to know which components handle progress updates, parameter changes, or new executions.
    - This makes the class reusable and easier to test, as the event handlers are external.

2. Scalability
    - Using an event bus multiple consumers to subscribe to TestCaseDataModel events, such as logging modules, analytics systems,
    or real-time UI updates.
    - This approach avoids direct coupling to specific consumers, making the system more extensible.

3. Real-Time Notifications
    - Directly publishing events when state changes (e.g., progress updates, parameter updates) allows for immediate system-wide reactions 
    without requiring synchronous or hard-coded connections.

4. Consistency Across Components
    - If other parts of the system also rely on the event bus for communication, using it in TestCaseDataModel ensures consistency in how data flows.

Cons
1. Responsibility Overlap
    - The TestCaseDataModel is primarily a data model. Introducing event us logic adds responsibilities related to communication, which can blur 
    its purpose.
    - This could lead to a violation of the single responsibility Principle.

2. Hidden Dependencies
    - By using the event bus, the TestCaseDataModel introduces implicit dependencies that re not obvious from its interface. This could make 
    debugging or testing more complex, as you'll need to mock or intercept the event bus.

3. Coupling to a Specific Event System
    - If the event bus implementation needs to change, all components (including the TestCaseDataModel) that directly interact with it must be 
    updated. This adds indirect coupling to the event bus.

4. Hard to Trade Flow
    - Events emitted from the TestCaseDataModel could be consumed by any number of components. This makes it harder to trace what happens when an
    event is published.


Does SystemEventBus make sense here?
Yes, if:
    - The system heavily relies on the SystemEventBus for communication, and events like ProgressUpdateEvent or ParameterUpdateEvent are system-wide concerns.
    - The TestCaseDataModel is tightly integrated into workflows where real-time updates and notifications are essential (e.g., updating UI, logging)

No, if
    - The event bus is only used sporadically for specific features, making it less of a core component.
    - The TestCaseDataModel is primarily used for data storage or retrieval without system-wide responsibilities.

    
Alternatices to Using Event Bus Inside TestCaseDataModel
1. Delegate Event Bus Interaction to TCNode
    - Keep the TestCaseDataModel focused on storing and managing test case data.
    - Let TCNode, which is already part of the workflow layer, handle publishing events when interacting with TestCaseDataModel

        # TCNode
        async def update_progress(self, progress: int):
            self._data_model.update_progress(progress)
            progress_update_event = ProgressUpdateEvent(self._data_model)
            await SystemEventBus.publish(progress_update_event)

2. Event Dispatcher Pattern
    - Introduce a lightweight dispatcher inside the TestcaseDataModel that components can subscribe to, avoiding reliance on the SystemEventBus.
    - This keeps the scope of event handling limited to the test case level.

        class TestCaseDataModel:
            def __init__(self, ...):
                self._subscribers = []

            def subscribe(self, callback: Callable):
                self._subscribers.append(callback)

            def notify_subscribers(self, event: str, data: Any):
                for callback in self._subscribers:
                    callback(event, data)

            async def update_progress(self, progress: int):
                self._progress = progress
                self.notify_subscribers("progress_updated", {"progress": progress})

3. Custom Observer for Workflow Events
    - Define a dedicated ovserver for workflow events, such as TestRunObserver or SystemNotifier, and pass it as a dependency to TestCaseDataModel.
        
        class TestCaseDataModel:
            def __init__(self, observer: "TestRunObserver"):
                self._observer = observer

            async def update_progress(self, progress: int):
                self._progress = progress
                await self._observer.on_progress_update(self)

Recommendation
If you plan to retain the SystemEventBus in TestCaseDataModel:
    1. Clearly document the purpose and events it publishes.
    2. Ensure it is central to the system's architecture (e.g., most components use if for communication).
    3. Avoid duplicating event publishing in multiple layers (e.g., TCNode and TestCaseDataModel both publishing the same event).

If you want to refactor:
    - Delegate event publishing to TCnode or another higher-level component, keeping TestCaseDataModel focused on managing test case data.
    

Make an EventPublisher object to decouple SystemEventBus away from TestCaseDataModel
"""