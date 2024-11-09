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
