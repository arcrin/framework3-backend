from typing import List, Any, Callable
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
  def __init__(self, name: str="Node") -> None:
    self._name = name
    self._dependencies: List["BaseNode"] = []
    self._state = NodeState.NOT_PROCESSED
    self._on_ready_callback: Callable[["BaseNode"], None] = lambda node: None
    self._result = None

  @property
  @abstractmethod
  def result(self) -> Any:
    raise NotImplementedError("result() not implemented")


  @property
  def name(self) -> str:
    return self._name
  
  @property
  def dependencies(self) -> List["BaseNode"]:
    return self._dependencies

  def add_dependency(self, node: "BaseNode") -> None:
    self._dependencies.append(node)
    # TODO: This is likely not the state we want to set here. Reconsider when we have more states
    self._state = NodeState.NOT_PROCESSED

  def remove_dependency(self, node: "BaseNode") -> None:
    self._dependencies.remove(node)

  def set_cleared(self) -> None:
    self._state = NodeState.CLEARED

  def is_cleared(self) -> bool:
    return self._state == NodeState.CLEARED
  
  def ready_to_process(self) -> bool:
    if all([node.is_cleared() for node in self._dependencies]):
      self._state = NodeState.READY_TO_PROCESS
      return True
    return False
  
  def notify_dependencies_resolved(self):
    if all(dep.is_cleared() for dep in self.dependencies):
      self._state = NodeState.READY_TO_PROCESS
      self._on_ready_callback(self)

  def set_on_ready_callback(self, callback: Callable[["BaseNode"], None]):
    self._on_ready_callback = callback  


  @abstractmethod
  async def execute(self) -> None:
    """
    Every node must have a execute() method. Based on the different job type, the implementation of this method will differ.
    """
    raise NotImplementedError("execute() not implemented")
    