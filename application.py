from producer_consumer.result_processor import ResultProcessor
from producer_consumer.node_executor import NodeExecutor
from sample_profile.profile import SampleTestProfile
from node.base_node import BaseNode
from typing import List, Dict
import trio


class Application:
    def __init__(self):
        self._nodes: List[BaseNode] = []
        self._persist_nodes: Dict[str, BaseNode] = {}
        
        self._node_executor_send_channel: trio.MemorySendChannel[BaseNode]
        self._node_executor_receive_channel: trio.MemoryReceiveChannel[BaseNode]
        self._node_executor_send_channel, self._node_executor_receive_channel = trio.open_memory_channel(50)

        self._result_processor_send_channel: trio.MemorySendChannel[BaseNode]
        self._result_processor_receive_channel: trio.MemoryReceiveChannel[BaseNode]
        self._result_processor_send_channel, self._result_processor_receive_channel = trio.open_memory_channel(50)

        self._node_executor: NodeExecutor = NodeExecutor(
            self._node_executor_receive_channel, self._result_processor_send_channel  # type: ignore
        )

        self._result_processor = ResultProcessor(self._result_processor_receive_channel) # type: ignore


    async def add_node(self, node: BaseNode):
        self._nodes.append(node)
        node.set_scheduling_callback(self._node_ready)
        await node.check_dependency_and_schedule_self()

    async def _node_ready(self, node: BaseNode):
        await self._node_executor_send_channel.send(node)

    async def load_test_case(self):
        # LoadProfileNode should happen first, and it will return a the test jig class and profile class.
        # test jig class is used to initialize the hardware configuration of the test jig, profile class
        # is used to initialize the test cases. I need to create the dependencies among all of these tasks
        # and put them into a list.

        # I need to check if a node is ready to be put on the execution queue. I need to find a way to get around this.
        # load_test_case = LoadTCNode(self._nodes, SampleProfile)
        # await self._queue_for_execution.put(load_test_case)
        profile = SampleTestProfile()
        for tc_node in profile.test_case_list:
            await self.add_node(tc_node)

    @property
    def nodes(self) -> List[BaseNode]:
        return self._nodes

    async def start(self):
        await self.load_test_case()
        # self._dependency_checker.start_processing()
        # self._node_executor.start_processing()
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self._node_executor.start)
            nursery.start_soon(self._result_processor.start)