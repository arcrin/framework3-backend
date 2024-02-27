from typing import List, Any, Callable, Awaitable
from abc import ABC, abstractmethod
from enum import Enum


class NodeState(Enum):
    READY_TO_PROCESS = 1
    CLEARED = 2
    NOT_PROCESSED = 3


class BaseNode(ABC):
    """
    A node represents a single unit of job.
    """

    def __init__(self, name: str = "Node") -> None:
        self._name = name
        self._dependencies: List["BaseNode"] = []
        self._dependents: List["BaseNode"] = []
        self._state = NodeState.NOT_PROCESSED
        self._on_ready_callback: Callable[
            ["BaseNode"], Awaitable[None]
        ] = self._default_on_ready_callback
        self._result = None

    @property
    @abstractmethod
    def result(self) -> Any:
        raise NotImplementedError("result() not implemented")

    @property
    def state(self) -> NodeState:
        return self._state

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
