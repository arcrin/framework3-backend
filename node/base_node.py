from typing import List, Any, Callable, Awaitable, Optional
from abc import ABC, abstractmethod
from enum import Enum


class NodeState(Enum):
    READY_TO_PROCESS = 1
    CLEARED = 2
    NOT_PROCESSED = 3
    ERROR = 4
    CANCELLED = 5


class BaseNode(ABC):
    """
    A node represents a single unit of job.
    """

    def __init__(self, name: str = "Node", 
                 func_parameter_label: str | None=None) -> None:
        self._name: str = name
        self._dependencies: List["BaseNode"] = []
        self._dependents: List["BaseNode"] = []
        self._state: NodeState = NodeState.NOT_PROCESSED
        self._on_ready_callback: Callable[
            ["BaseNode"], Awaitable[None]
        ] = self._default_on_ready_callback
        self._result: Any = None
        self._error: Optional[Exception] = None
        self._error_traceback: Optional[str] = ""
        self._func_parameter_label: str | None = func_parameter_label

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
    def func_parameter_label(self) -> str:
        if self._func_parameter_label is None:
            raise ValueError("func_parameter_label is not set")
        return self._func_parameter_label

    @property
    def state(self) -> NodeState:
        return self._state
    
    @state.setter
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
    def on_ready_callback(self) -> Callable[["BaseNode"], Awaitable[None]]:
        return self._on_ready_callback

    async def _default_on_ready_callback(self, node: "BaseNode") -> None:
        pass

    def add_dependency(self, node: "BaseNode") -> None:
        if self._is_reachable(node):
            raise ValueError("Cyclic dependency detected")
        self._dependencies.append(node)
        node._dependents.append(self)
        self._state = NodeState.NOT_PROCESSED

    def remove_dependency(self, node: "BaseNode") -> None:
        self._dependencies.remove(node)
        node._dependents.remove(self)

    async def set_cleared(self) -> None:
        self._state = NodeState.CLEARED
        for dep in self._dependents:
            await dep.notify_dependencies_resolved()

    def is_cleared(self) -> bool:
        return self._state == NodeState.CLEARED

    def ready_to_process(self) -> bool:
        if all([node.is_cleared() for node in self._dependencies]):
            self._state = NodeState.READY_TO_PROCESS
            return True
        return False

    async def notify_dependencies_resolved(self) -> None:
        if all(dep.is_cleared() for dep in self.dependencies):
            self._state = NodeState.READY_TO_PROCESS
            await self._on_ready_callback(self)

    def set_on_ready_callback(
        self, callback: Callable[["BaseNode"], Awaitable[None]]
    ) -> None:
        self._on_ready_callback = callback

    async def reset(self) -> None:
        self._state = NodeState.NOT_PROCESSED
        self._result = None
        await self.notify_dependencies_resolved()
        for dependency in self.dependents:
            await dependency.reset()

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
