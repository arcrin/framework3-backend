#type: ignore
from producer_consumer.result_processor import ResultProcessor
from producer_consumer.node_executor import NodeExecutor
from producer_consumer.log_processor import LogProcessor
from sample_profile.profile import SampleTestProfile
from node.base_node import BaseNode
from typing import List, Dict, Set
from trio_websocket import ConnectionClosed, serve_websocket
from util.log_handler import WebSocketLogHandler
from util.log_filter import TAGAppLoggerFilter
from queue import Queue
import math
import logging
import trio


class Application:
    def __init__(self):
        self._nodes: List[BaseNode] = []
        self._persist_nodes: Dict[str, BaseNode] = {}
        self._ws_connections = set()
        self._ws_server_cancel_scope: trio.CancelScope = trio.CancelScope()
        
        self._node_executor_send_channel: trio.MemorySendChannel[BaseNode]
        self._node_executor_receive_channel: trio.MemoryReceiveChannel[BaseNode]
        self._node_executor_send_channel, self._node_executor_receive_channel = trio.open_memory_channel(50)

        self._result_processor_send_channel: trio.MemorySendChannel[BaseNode]
        self._result_processor_receive_channel: trio.MemoryReceiveChannel[BaseNode]
        self._result_processor_send_channel, self._result_processor_receive_channel = trio.open_memory_channel(50)

        self._log_queue: Queue[logging.LogRecord] = Queue()
        root_logger = logging.getLogger()   
        ws_logger_handler = WebSocketLogHandler(self._log_queue)
        if root_logger.handlers:
            formatter = root_logger.handlers[0].formatter
            ws_logger_handler.setFormatter(formatter)
        ws_logger_handler.addFilter(TAGAppLoggerFilter())
        ws_logger_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(ws_logger_handler)

        self._node_executor: NodeExecutor = NodeExecutor(self._node_executor_receive_channel, self._result_processor_send_channel)  # type: ignore
        self._result_processor = ResultProcessor(self._result_processor_receive_channel) # type: ignore
        self._log_processor = LogProcessor(self._log_queue, self._ws_connections) # type: ignore

    async def add_node(self, node: BaseNode):
        self._nodes.append(node)
        node.set_scheduling_callback(self._node_ready)
        await node.check_dependency_and_schedule_self()

    async def _node_ready(self, node: BaseNode):
        await self._node_executor_send_channel.send(node)

    async def load_test_case(self):
        profile = SampleTestProfile()
        for tc_node in profile.test_case_list:
            await self.add_node(tc_node)

    async def start_ws(self):
        async def ws_connection_handler(request):
            ws = await request.accept()
            self._ws_connections.add(ws)
            print(f"WS connection established with:{ws}")
            while True:
                try:
                    await ws.get_message()  
                except ConnectionClosed:
                    print(f"WS connection closed with {ws}")
                    self._ws_connections.remove(ws)   
                    self._ws_server_cancel_scope.cancel()
                    self._log_processor.stop()
                    print("WS server stopped")
        self._ws_server_cancel_scope = trio.CancelScope()
        with self._ws_server_cancel_scope:
            await serve_websocket(ws_connection_handler, "localhost", 8000, ssl_context=None)
        

    @property
    def nodes(self) -> List[BaseNode]:
        return self._nodes

    async def start(self):
        await self.load_test_case()
        
        try:
            async with trio.open_nursery() as nursery:
                nursery.start_soon(self.start_ws)
                nursery.start_soon(self._node_executor.start)
                nursery.start_soon(self._result_processor.start)
                nursery.start_soon(self._log_processor.start) 
        except Exception as e:
            print(e)
            raise