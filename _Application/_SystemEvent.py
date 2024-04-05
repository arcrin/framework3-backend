from abc import ABC


class BaseEvent(ABC):
    def __init__(self, payload):  # type: ignore
        self._payload = payload

    @property
    def payload(self):
        return self._payload


class NewTestCaseEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)


class NewTestExecutionEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)


class ParameterUpdateEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)


class ProgressUpdateEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)

class TestCaseFailEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)   


class TestRunTerminationEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)