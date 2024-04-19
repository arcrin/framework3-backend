from abc import ABC
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from _Node._BaseNode import BaseNode
    from _Node._TCNode import TCNode
    from _Application._DomainEntity._TestCaseDataModel import TestCaseDataModel
    from _Application._DomainEntity._InteractionContext import InteractionContext


class BaseEvent(ABC):
    def __init__(self, payload):  # type: ignore
        self._payload = payload

    @property
    def payload(self):
        return self._payload


class NewTestCaseEvent(BaseEvent):
    def __init__(self, payload: "TCNode"):  
        super().__init__(payload)

class NodeReadyEvent(BaseEvent):
    def __init__(self, payload: "BaseNode"):
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
    def __init__(self, payload: "InteractionContext"): 
        super().__init__(payload)

class UserResponseEvent(BaseEvent):
    def __init__(self, payload: Dict[str, str]):  # type: ignore
        super().__init__(payload)