from typing import List, TYPE_CHECKING
from datetime import datetime
from _Application._DomainEntity._Parameter import Parameter
from _Application._SystemEvent import ParameterUpdateEvent

if TYPE_CHECKING:
    from _SystemEventBus import SystemEventBus
    from _Application._DomainEntity._TestRun import TestRun


class TestRepetition:
    def __init__(
        self,
        repetition_count: int,
        timestamp: datetime,
    ):
        self._repetition_count: int = repetition_count
        self._timestamp: datetime = timestamp
        self._test_duration: float = 0.0
        self._parameters: List[Parameter] = []

    @property
    def repetition_count(self) -> int:
        return self._repetition_count

    @repetition_count.setter
    def repetition_count(self, value: int):
        self._repetition_count = value

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
        self._repetition: List[TestRepetition] = []
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

    async def add_repetition(self):
        repetition = TestRepetition(len(self._repetition), datetime.now())
        self._repetition.append(repetition)
        # TODO: add NewTestRepetitionEvent

    async def update_parameter(self, parameter: Parameter):
        assert self.event_bus is not None, "TCNode must be connected to a system event bus"
        self._repetition[-1].update_parameter(parameter)
        # TODO: add NewParameterEvent

        parameter_update_event = ParameterUpdateEvent(
            {"tc_id": self._tc_id, "parameter": {parameter.name: parameter.as_dict()}} # type: ignore
        )
        await self.event_bus.publish(parameter_update_event)
