from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _Node._TCNode import TCNode
    from _Application._DomainEntity._TestCaseDataModel import TestCaseDataModel


class BaseEvent(ABC):
    def __init__(self, payload):  # type: ignore
        self._payload = payload

    @property
    def payload(self):
        return self._payload


class NewTestCaseEvent(BaseEvent):
    def __init__(self, payload: "TCNode"):  
        super().__init__(payload)


class NewTestExecutionEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)


class ParameterUpdateEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)


class ProgressUpdateEvent(BaseEvent):
    def __init__(self, payload: "TestCaseDataModel"):
        super().__init__(payload)

class TestCaseFailEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)   


class TestRunTerminationEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)

class UserInteractionEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)