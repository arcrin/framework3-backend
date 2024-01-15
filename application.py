from node.base_node import BaseNode
# from node.load_profile_node import LoadProfileNode
# from node.product_info_node import ProductInfoNode
# from node.tj_config_node import TJConfigNode
# from node.executable_node import ExecutableNode
from sample_profile.profile import SampleProfile
from node.load_test_case_node import LoadTestCaseNode
from typing import List, Dict
from producer_consumer.node_executor import NodeExecutor
from producer_consumer.dependency_checker import DependencyChecker
import asyncio

class Application:
  def __init__(self):
    self._nodes: List[BaseNode] = []
    self._persist_nodes: Dict[str, BaseNode] = {}
    self._queue_for_executable_nodes: asyncio.Queue[BaseNode] = asyncio.Queue()
    self._queue_for_result_processing: asyncio.Queue[BaseNode] = asyncio.Queue()
    self._node_executor: NodeExecutor = NodeExecutor(self._queue_for_executable_nodes, 
                                                     self._queue_for_result_processing)
    self._dependency_checker: DependencyChecker = DependencyChecker(self._nodes, self._queue_for_executable_nodes)
    
  async def load_test_case(self):
    # LoadProfileNode should happen first, and it will return a the test jig class and profile class. 
    # test jig class is used to initialize the hardware configuration of the test jig, profile class
    # is used to initialize the test cases. I need to create the dependencies among all of these tasks
    # and put them into a list.

    # I need to check if a node is ready to be put on the execution queue. I need to find a way to get around this.
    load_test_case = LoadTestCaseNode(self._nodes, SampleProfile)
    await self._queue_for_executable_nodes.put(load_test_case)
     
  @property
  def nodes(self) -> List[BaseNode]:
    return self._nodes
  
  async def start(self):
    await self.load_test_case()
    # self._dependency_checker.start_processing()
    # self._node_executor.start_processing()
    await asyncio.gather(self._dependency_checker.start_processing(), self._node_executor.start_processing())
  
