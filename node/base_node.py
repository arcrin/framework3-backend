from typing import List

class BaseNode:
  def __init__(self, name: str="Node") -> None:
    self._name = name
    self._dependencies: List["BaseNode"] = []


  @property
  def name(self) -> str:
    return self._name
  
  @property
  def dependencies(self) -> List["BaseNode"]:
    return self._dependencies

  def add_dependency(self, node: "BaseNode") -> None:
    self._dependencies.append(node)

  def remove_dependency(self, node: "BaseNode") -> None:
    self._dependencies.remove(node)
    