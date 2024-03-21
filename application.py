from producer_consumer.result_processor import ResultProcessor
from producer_consumer.node_executor import NodeExecutor
from producer_consumer.log_processor import LogProcessor
from producer_consumer.ui_request_processor import UIRequestProcessor
from producer_consumer.tc_data_ws_processor import TCDataWSProcessor
from producer_consumer.app_command_processor import AppCommandProcessor
from sample_profile.profile import SampleTestProfile
from node.base_node import BaseNode
from node.tc_node import TCNode
from node.terminal_node import TerminalNode
from typing import List, Dict, Set, Any
from util.log_handler import WebSocketLogHandler
from util.log_filter import TAGAppLoggerFilter
from util.tc_data_broker import TCDataBroker
from comm_modules.ws_comm_module import WSCommModule
from queue import Queue
import trio_websocket # type: ignore
import logging
import trio


class Application:
    def __init__(self):
        self._nodes: List[BaseNode] = []
        self._persist_nodes: Dict[str, BaseNode] = {}
        self._ws_connections: Set[trio_websocket.WebSocketConnection] = set()
        self._ws_server_cancel_scope: trio.CancelScope = trio.CancelScope()
        self._main_connection: trio_websocket.WebSocketConnection  # REMOVE
        self._command_mapping = {
            "loadTC": self.load_test_case,
        }

        self._node_executor_send_channel: trio.MemorySendChannel[BaseNode]
        self._node_executor_receive_channel: trio.MemoryReceiveChannel[BaseNode]
        self._node_executor_send_channel, self._node_executor_receive_channel = (
            trio.open_memory_channel(50)
        )

        self._result_processor_send_channel: trio.MemorySendChannel[BaseNode]
        self._result_processor_receive_channel: trio.MemoryReceiveChannel[BaseNode]
        self._result_processor_send_channel, self._result_processor_receive_channel = (
            trio.open_memory_channel(50)
        )

        self._app_command_send_channel: trio.MemorySendChannel[str]
        self._app_command_receive_channel: trio.MemoryReceiveChannel[str]
        self._app_command_send_channel, self._app_command_receive_channel = (
            trio.open_memory_channel(50)
        )

        self._ui_request_send_channel: trio.MemorySendChannel[str]
        self._ui_request_receive_channel: trio.MemoryReceiveChannel[str]
        self._ui_request_send_channel, self._ui_request_receive_channel = (
            trio.open_memory_channel(50)
        )

        self._ui_response_send_channel: trio.MemorySendChannel[str]
        self._ui_response_receive_channel: trio.MemoryReceiveChannel[str]
        self._ui_response_send_channel, self._ui_response_receive_channel = (
            trio.open_memory_channel(50)
        )

        self._tc_data_send_channel: trio.MemorySendChannel[List[Any]]
        self._tc_data_receive_channel: trio.MemoryReceiveChannel[List[Any]]
        self._tc_data_send_channel, self._tc_data_receive_channel = (
            trio.open_memory_channel(50)
        )

        # COMMENT: Initialize communication modules
        self._ws_comm_module = WSCommModule(
            self._app_command_send_channel, self._ui_response_send_channel # type: ignore
        )
        # COMMENT: Custom log handler and filter installation
        self._log_queue: Queue[logging.LogRecord | TerminalNode] = Queue()
        root_logger = logging.getLogger()
        ws_logger_handler = WebSocketLogHandler(self._log_queue)
        if root_logger.handlers:
            formatter = root_logger.handlers[0].formatter
            ws_logger_handler.setFormatter(formatter)
        ws_logger_handler.addFilter(TAGAppLoggerFilter())
        ws_logger_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(ws_logger_handler)

        # COMMENT: Consumer initialization
        self._node_executor: NodeExecutor = NodeExecutor(
            self._node_executor_receive_channel,  # type: ignore
            self._result_processor_send_channel,  # type: ignore
        )
        self._result_processor = ResultProcessor(self._result_processor_receive_channel)  # type: ignore
        self._log_processor = LogProcessor(self._log_queue, self._ws_comm_module)  
        self._ui_request_processor = UIRequestProcessor(
            self._ui_request_receive_channel, self._ui_response_receive_channel, self._ws_comm_module # type: ignore
        )
        self._tc_data_ws_processor = TCDataWSProcessor(self._tc_data_receive_channel, self._ws_comm_module) # type: ignore

        self._app_command_processor = AppCommandProcessor(
            self._app_command_receive_channel, self._command_mapping # type: ignore
        )

        self._tc_data = []

        self._logger = logging.getLogger("Application")

    async def add_node(self, node: BaseNode):
        # TODO: where am I adding these node to?
        self._nodes.append(node)
        node.set_scheduling_callback(self._node_ready)
        node.ui_request_send_channel = self._ui_request_send_channel
        if isinstance(node, TCNode):
            tc_data_broker = TCDataBroker(self._tc_data_send_channel, self._tc_data) # type: ignore
            node.tc_data_broker = tc_data_broker
        await node.check_dependency_and_schedule_self()

    async def _node_ready(self, node: BaseNode):
        await self._node_executor_send_channel.send(node)

    async def load_test_case(self):
        profile = SampleTestProfile()
        for tc_node in profile.test_case_list:
            await self.add_node(tc_node)

    @property
    def nodes(self) -> List[BaseNode]:
        return self._nodes

    async def start(self):
        try:
            async with trio.open_nursery() as nursery:
                # NOTE: Each consumer can be considered as an attachment
                nursery.start_soon(self._ws_comm_module.start_server)
                nursery.start_soon(self._node_executor.start)
                nursery.start_soon(self._result_processor.start)
                nursery.start_soon(self._log_processor.start)
                nursery.start_soon(self._ui_request_processor.start)
                nursery.start_soon(self._tc_data_ws_processor.start)
                nursery.start_soon(self._app_command_processor.start)
        except Exception as e:
            self._logger.error(e)
            raise
