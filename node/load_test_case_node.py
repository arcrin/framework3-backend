from node.base_node import BaseNode
from typing import List, Type, Any

class LoadTCNode(BaseNode):
  def __init__(self, node_list: List[BaseNode], profile_class: Type[Any]) -> None:
    super().__init__("LoadTestCaseNode")
    self._profile_class = profile_class
    self._node_list = node_list

  async def execute(self):
    profile_instance = self._profile_class()
    self._node_list.extend(profile_instance.test_case_list)

  @property
  def result(self):
    return self._result