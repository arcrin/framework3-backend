from _Application._SystemEventBus import SystemEventBus
from _Application._SystemEvent import NodeReadyEvent
from typing import List, Any, Optional
from abc import ABC, abstractmethod
from enum import Enum
from uuid import uuid4
import logging


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
        func_parameter_label: str | None = None
    ) -> None:
        self._name: str = name
        self._dependencies: List["BaseNode"] = []
        self._dependents: List["BaseNode"] = []
        self._state: NodeState = NodeState.NOT_PROCESSED
        self._result: Any = None
        self._error: Optional[Exception] = None
        self._error_traceback: Optional[str] = ""
        self._func_parameter_label: str | None = func_parameter_label
        self._logger = logging.getLogger("BaseNode")
        self._logger.setLevel(logging.DEBUG)
        self._id = uuid4().hex


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
    
    def mark_as_failed(self) -> None:
        self.state = NodeState.FAILED   

    def mark_as_passed(self) -> None:
        self.state = NodeState.PASSED
    
    def mark_as_not_processed(self) -> None:
        self.state = NodeState.NOT_PROCESSED

    def mark_as_processing(self) -> None:
        self.state = NodeState.PROCESSING

    def mark_as_cleared(self) -> None:
        self.state = NodeState.CLEARED
    

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
                # await self._scheduling_callback(self)
                node_ready_event = NodeReadyEvent(self)
                await SystemEventBus.publish(node_ready_event)
                self._logger.info(f"{self.name} is scheduled")
            except Exception as e:
                self._logger.error(
                    f"Error while scheduling {self.name}: {e}", exc_info=True
                )
                raise

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

"""
Key Elements in BaseNode
    1. State Management with NodeState: Using an enum to manage the different states of each node (job) is a solid approach. 
    This helps ensure consistency across different node types, with states like READY_TO_PROCESS, CLEARED, PROCESSING, etc.
    2. Dependency Management: The methods add_dependency, remove_dependency, and _is_reachable provide a way to set and validate
    dependencies while also avoiding cyclic dependencies, which is critical for DAGs. 
    3. Execution Control: 
        - The ready_to_process and check_dependency_and_schedule_self methods control when nodes become ready based on the state
        of their dependencies.
        - Using an event bus (SystemEventBus.publish) to notify other parts of the system when a node is erady aligns well with the 
        Producer-Consumer pattern.
        - The execute method is abstract, allowing subclasses to implement specific job-related functionality.
    4. Asynchronous Operations: Trio's compatibility with async functions fits well here, especially with methods like reset, set_cleared,
    and check_dependency_and_schedule_self. Trio's structured concurrency model should handle these async dependencies cleanly.
    5. Error Handling: error and error_traceback properties allow tracking issues within nodes, which could simplify debugging and error 
    reporting in the overall job flow.
    6. Logging: Integrating logging into various methods provides clean traceability of state changes, dependency handling, and scheduling,
    which is essential for debugging and performance monitoring.

Potential Areas for Consideration
    - Async Execution Flow: in Trio, tasks like dependent.reset() within reset might indeed benefit from a structured way to handle 
    concurrent resets, such as with a nursery.
    - Parameter Passing: The comment about func_parameter_label indicates some uncertainty. This attribute could potentially evolve, 
    depending on how parameters are handled in specific node implementations.
    - Event Bus Dependency: Relying on SystemEventBus means there's some coupling to the event system, which may require flexibility if 
    the event handling mechanism needs to evolve.
"""