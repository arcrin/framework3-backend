from _ProducerConsumer._WorkflowProcessor._ResultProcessor import ResultProcessor
from _ProducerConsumer._WorkflowProcessor._NodeExecutor import NodeExecutor
from _ProducerConsumer._SideEffectProcessor._AppCommandProcessor import (
    AppCommandProcessor,
)
from _ProducerConsumer._SideEffectProcessor._UIRequestProcessor import (
    UIRequestProcessor,
)
from _ProducerConsumer._SideEffectProcessor._TCDataWSProcessor import TCDataWSProcessor
from _ProducerConsumer._SideEffectProcessor._LogProcessor import LogProcessor
from _Application._SystemEventBus import SystemEventBus
from _Application._AppStateManager import ApplicationStateManager
from _CommunicationModules._WSCommModule import WSCommModule
from sample_profile.profile import SampleTestProfile
from util.log_handler import WebSocketLogHandler
from util.log_filter import TAGAppLoggerFilter
from _Node._TerminalNode import TerminalNode

from typing import Dict, Any, TYPE_CHECKING
from queue import Queue
import logging
import trio

if TYPE_CHECKING:
    from _Node._BaseNode import BaseNode


class Application:
    def __init__(self):
        self._command_mapping = {
            "loadTC": self.start_test_run,
        }

        self._node_executor_send_channel: trio.MemorySendChannel["BaseNode"]
        self._node_executor_receive_channel: trio.MemoryReceiveChannel["BaseNode"]
        self._node_executor_send_channel, self._node_executor_receive_channel = (
            trio.open_memory_channel["BaseNode"](50)
        )

        self._result_processor_send_channel: trio.MemorySendChannel["BaseNode"]
        self._result_processor_receive_channel: trio.MemoryReceiveChannel["BaseNode"]
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

        self._tc_data_send_channel: trio.MemorySendChannel[Dict[Any, Any]]
        self._tc_data_receive_channel: trio.MemoryReceiveChannel[Dict[Any, Any]]
        self._tc_data_send_channel, self._tc_data_receive_channel = (
            trio.open_memory_channel[Dict[Any, Any]](50)
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

        # COMMENT: Application state manager initialization
        self._system_event_bus = SystemEventBus()
        self._asm = ApplicationStateManager(self._system_event_bus, 
                                    self._tc_data_send_channel, # type: ignore 
                                    self._node_executor_send_channel, # type: ignore
                                    self._ui_request_send_channel, # type: ignore
                                    SampleTestProfile)

        # COMMENT: Consumer initialization

        # COMMENT: Initialize communication modules
        self._ws_comm_module = WSCommModule(
            self._app_command_send_channel,  # type: ignore
            self._ui_response_send_channel,  # type: ignore
            self._asm,
        )

        self._node_executor: NodeExecutor = NodeExecutor(
            self._node_executor_receive_channel,  # type: ignore
            self._result_processor_send_channel,  # type: ignore
        )
        self._result_processor = ResultProcessor(self._result_processor_receive_channel)  # type: ignore
        self._log_processor = LogProcessor(self._log_queue, self._ws_comm_module)
        self._ui_request_processor = UIRequestProcessor(
            self._ui_request_receive_channel,  # type: ignore
            self._ui_response_receive_channel,  # type: ignore
            self._ws_comm_module,
        )
        self._tc_data_ws_processor = TCDataWSProcessor(
            self._tc_data_receive_channel,  # type: ignore
            self._ws_comm_module,
        )

        self._app_command_processor = AppCommandProcessor(
            self._app_command_receive_channel,  # type: ignore
            self._command_mapping,
        )
                                 
        self._logger = logging.getLogger("Application")

    async def start_test_run(self):
        if self._asm.control_session is None:
            self._logger.error("Control session not established")
            raise Exception(
                "Control session not established"
            )  # TODO: this should not stop the application execution loop, prompt user instead
        for panel in self._asm.control_session.panels:
            await panel.add_test_run()
            if panel.test_run is not None:
                await panel.test_run.load_test_case()

    async def start(self):
        try:
            async with trio.open_nursery() as nursery:
                # NOTE: Each consumer can be considered as an attachment
                nursery.start_soon(self._ws_comm_module.start)
                nursery.start_soon(self._node_executor.start)
                nursery.start_soon(self._result_processor.start)
                nursery.start_soon(self._log_processor.start)
                nursery.start_soon(self._ui_request_processor.start)
                nursery.start_soon(self._tc_data_ws_processor.start)
                nursery.start_soon(self._app_command_processor.start)
        except Exception as e:
            self._logger.error(e)
            raise
