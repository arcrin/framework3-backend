from typing import List, Any, Callable, Awaitable, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
from enum import Enum
from uuid import uuid4
import trio
import logging

if TYPE_CHECKING:
    from _Application._SystemEventBus import SystemEventBus


class NodeState(Enum):
    READY_TO_PROCESS = "ready_to_process"
    CLEARED = "cleared"
    NOT_PROCESSED = "not_processed"
    CANCEL = "cancel"
    ERROR = "error"
    PROCESSING = "processing"
    PASSED = "passed"
    FAILED = "failed"


class BaseNode(ABC):
    """
    A node represents a single unit of job.
    """

    def __init__(
        self, 
        name: str,
        event_bus: "SystemEventBus | None" = None,
        func_parameter_label: str | None = None
    ) -> None:
        self._name: str = name
        self._dependencies: List["BaseNode"] = []
        self._dependents: List["BaseNode"] = []
        self._state: NodeState = NodeState.NOT_PROCESSED
        self._scheduling_callback: Callable[["BaseNode"], Awaitable[None]] = (
            self._default_on_ready_callback
        )
        self._result: Any = None
        self._error: Optional[Exception] = None
        self._error_traceback: Optional[str] = ""
        self._func_parameter_label: str | None = func_parameter_label
        self._logger = logging.getLogger("BaseNode")
        self._logger.setLevel(logging.DEBUG)
        self._ui_request_send_channel: trio.MemorySendChannel[str]
        self._event_bus: "SystemEventBus | None" = event_bus
        self._id = uuid4().hex

    @property
    def event_bus(self) -> "SystemEventBus | None":
        return self._event_bus
    
    @event_bus.setter
    def event_bus(self, value: "SystemEventBus"):
        self._event_bus = value

    @property
    def id(self):
        return self._id

    @property
    def result(self) -> Any:
        return self._result

    @property
    def error(self) -> Optional[Exception]:
        return self._error

    @error.setter
    def error(self, value: Optional[Exception]) -> None:
        self.state = NodeState.ERROR
        self._error = value

    # TODO: Explore a different way to pass parameters, at least a better name for this attribute
    @property
    def func_parameter_label(self) -> str | None:
        return self._func_parameter_label

    @property
    @abstractmethod
    def state(self) -> NodeState:
        return self._state

    @state.setter
    @abstractmethod
    def state(self, value: NodeState) -> None:
        self._state = value

    @property
    def error_traceback(self) -> Optional[str]:
        return self._error_traceback

    @error_traceback.setter
    def error_traceback(self, value: Optional[str]) -> None:
        self._error_traceback = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def dependencies(self) -> List["BaseNode"]:
        return self._dependencies

    @property
    def dependents(self) -> List["BaseNode"]:
        return self._dependents

    @property
    def scheduling_callback(self) -> Callable[["BaseNode"], Awaitable[None]]:
        return self._scheduling_callback

    async def _default_on_ready_callback(self, node: "BaseNode") -> None:
        pass

    def add_dependency(self, node: "BaseNode") -> None:
        if self._is_reachable(node):
            raise ValueError("Cyclic dependency detected")
        if node in self._dependencies:
            self._logger.info(f"{node.name} is already a dependency to {self.name}")
            return
        self._dependencies.append(node)
        node._dependents.append(self)
        self._logger.info(f"{node.name} added as a dependency to {self.name}")
        self.state = NodeState.NOT_PROCESSED

    def remove_dependency(self, node: "BaseNode") -> None:
        self._logger.info(f"{node.name} removed as a dependency to {self.name}")
        self._dependencies.remove(node)
        node._dependents.remove(self)

    # COMMENT: when a node is cleared, notify all dependents
    async def set_cleared(self) -> None:
        self._logger.info(f"{self.name} node is cleared")
        self.state = NodeState.CLEARED
        for dep in self._dependents:
            await dep.check_dependency_and_schedule_self()

    def is_cleared(self) -> bool:
        return self.state == NodeState.CLEARED

    def ready_to_process(self) -> bool:
        if all([node.is_cleared() for node in self._dependencies]):
            self.state = NodeState.READY_TO_PROCESS
            self._logger.info(f"{self.name} is ready to process")
            return True
        return False

    async def check_dependency_and_schedule_self(self) -> None:
        if all(dep.is_cleared() for dep in self.dependencies):
            self._logger.info(f"{self.name} is ready to process")
            self.state = NodeState.READY_TO_PROCESS
            # TODO: This needs to be handled atop
            try:
                await self._scheduling_callback(self)
                self._logger.info(f"{self.name} is scheduled")
            except Exception as e:
                self._logger.error(
                    f"Error while scheduling {self.name}: {e}", exc_info=True
                )
                raise

    def set_scheduling_callback(
        self, callback: Callable[["BaseNode"], Awaitable[None]]
    ) -> None:
        self._scheduling_callback = callback

    async def reset(self) -> None:
        # COMMENT: If the node is processing, label is set as CANCELLED. 
        #   Its results upon completion will be ignored and the node will be rescheduled. 
        #   The result processing consumer should change the
        if self.state == NodeState.PROCESSING:
            self.state = NodeState.CANCEL
            self._logger.info(f"{self.name} node cancelled.")
        else:
            self.state = NodeState.NOT_PROCESSED
            self._result = None
            self._logger.info(f"{self.name} node reset.")
            # TODO: determine if this needs to be in a try block
            await self.check_dependency_and_schedule_self()
        for dependent in self.dependents:
            # TODO: Should this be inside a nursery?
            await dependent.reset()

    @abstractmethod
    async def execute(self) -> None:
        """
        Every node must have a execute() method. Based on the different job type, the implementation of this method will differ.
        """
        raise NotImplementedError("execute() not implemented")

    def _is_reachable(self, node: "BaseNode") -> bool:
        visited: set["BaseNode"] = set()

        def _dfs(current_node: "BaseNode"):
            if current_node == node:
                return True
            visited.add(current_node)
            for dependent in current_node.dependents:
                if dependent not in visited and _dfs(dependent):
                    return True
            return False

        return _dfs(self)
