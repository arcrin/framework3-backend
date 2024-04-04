from typing import List, TYPE_CHECKING
from datetime import datetime
from _Application._DomainEntity._Parameter import Parameter
from _Application._SystemEvent import (
    ParameterUpdateEvent, 
    ProgressUpdateEvent,
    NewTestExecutionEvent
    )

if TYPE_CHECKING:
    from _SystemEventBus import SystemEventBus
    from _Application._DomainEntity._TestRun import TestRun


class TestExecution:
    def __init__(
        self,
        execution_id: int,
    ):
        self._execution_id: int = execution_id
        self._timestamp: datetime = datetime.now()
        self._test_duration: float = 0.0
        self._parameters: List[Parameter] = []

    @property
    def execution_id(self) -> int:
        return self._execution_id

    @execution_id.setter
    def execution_id(self, value: int):
        self._execution_id = value

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
        self._event_bus: "SystemEventBus | None" = None
        self._parent_test_run: "TestRun | None" = None

    @property
    def event_bus(self) -> "SystemEventBus | None":
        return self._event_bus

    @event_bus.setter
    def event_bus(self, value: "SystemEventBus | None"):
        self._event_bus = value

    @property
    def parent_test_run(self) -> "TestRun | None":
        return self._parent_test_run

    @parent_test_run.setter
    def parent_test_run(self, value: "TestRun"):
        if not self._parent_test_run:
            self._parent_test_run = value
        else:
            raise Exception("A TCNode can only have one parent TestRun")
        
    @property
    def current_execution(self) -> TestExecution:
        return self._execution[-1]

    async def add_execution(self):
        assert (
            self.event_bus is not None
        ), "TCNode must be connected to a system event bus"
        execution = TestExecution(len(self._execution))
        self._execution.append(execution)
        new_test_execution_event = NewTestExecutionEvent(
            {"tc_id": self._tc_id, "execution_id": execution.execution_id}
        )
        await self.event_bus.publish(new_test_execution_event)

    async def update_parameter(self, parameter: Parameter):
        assert (
            self.event_bus is not None
        ), "TCNode must be connected to a system event bus"
        assert len(self._execution) > 0, "No execution to update parameter"
        self.current_execution.update_parameter(parameter)

        parameter_update_event = ParameterUpdateEvent(
            {"tc_id": self._tc_id, 
             "execution_id": self.current_execution.execution_id,
             "parameter": {parameter.name: parameter.as_dict()}}  # type: ignore
        )
        await self.event_bus.publish(parameter_update_event)

    async def update_progress(self, progress: int):
        assert (
            self.event_bus is not None
        ), "TCNode must be connected to a system event bus"
        progress_update_event = ProgressUpdateEvent(
            {"tc_id": self._tc_id, "progress": progress}
        )
        await self.event_bus.publish(progress_update_event)
