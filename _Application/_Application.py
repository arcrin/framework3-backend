from _ProducerConsumer._WorkflowProcessor._NodeResultProcessor import (
    NodeResultProcessor,
)
from _ProducerConsumer._WorkflowProcessor._NodeExecutor import NodeExecutor
from _ProducerConsumer._SideEffectProcessor._AppCommandProcessor import (
    AppCommandProcessor,
)
from _ProducerConsumer._SideEffectProcessor._UIRequestProcessor import (
    UIRequestProcessor,
)
from _ProducerConsumer._WorkflowProcessor._NodeFailureProcessor import (
    NodeFailureProcessor,
)
from _ProducerConsumer._SideEffectProcessor._UIResponseProcessor import (
    UIResponseProcessor,
)
from _ProducerConsumer._SideEffectProcessor._TCDataWSProcessor import TCDataWSProcessor
from _ProducerConsumer._SideEffectProcessor._LogProcessor import LogProcessor
from _Application._AppStateManager import ApplicationStateManager
from _Communication._WSCommModule import WSCommModule
from sample_profile.profile import SampleTestProfile
from util.log_handler import WebSocketLogHandler
from util.log_filter import TAGAppLoggerFilter
from _Node._TestRunTerminalNode import TestRunTerminalNode

from typing import Dict, Any, Tuple, TYPE_CHECKING
from queue import Queue
import logging
import trio

if TYPE_CHECKING:
    from _Node._BaseNode import BaseNode


class Application:
    def __init__(self,
                node_executor_channels: Tuple[trio.MemorySendChannel["BaseNode"], trio.MemoryReceiveChannel["BaseNode"]],
                node_result_processor_channels: Tuple[trio.MemorySendChannel["BaseNode"], trio.MemoryReceiveChannel["BaseNode"]],
                node_failure_channels: Tuple[trio.MemorySendChannel["BaseNode"], trio.MemoryReceiveChannel["BaseNode"]],
                app_command_channels: Tuple[trio.MemorySendChannel[Dict[Any, Any]], trio.MemoryReceiveChannel[Dict[Any, Any]]],
                ui_request_channels: Tuple[trio.MemorySendChannel[str], trio.MemoryReceiveChannel[str]],
                ui_response_channels: Tuple[trio.MemorySendChannel[str], trio.MemoryReceiveChannel[str]], 
                tc_data_channels: Tuple[trio.MemorySendChannel[Dict[Any, Any]], trio.MemoryReceiveChannel[Dict[Any, Any]]],
                ):
        self._command_mapping: Dict[Any, Any] = {
            "loadTC": self.start_test_run,
            "retest": self.retest,
        }
        #TODO: these channels could be dependencies passed into Application object during init
        self._node_executor_send_channel: trio.MemorySendChannel["BaseNode"]
        self._node_executor_receive_channel: trio.MemoryReceiveChannel["BaseNode"]
        self._node_executor_send_channel, self._node_executor_receive_channel = node_executor_channels 

        self._node_result_processor_send_channel: trio.MemorySendChannel["BaseNode"]
        self._node_result_processor_receive_channel: trio.MemoryReceiveChannel["BaseNode"]
        self._node_result_processor_send_channel, self._node_result_processor_receive_channel = node_result_processor_channels

        self._node_failure_send_channel: trio.MemorySendChannel["BaseNode"]
        self._node_failure_receive_channel: trio.MemoryReceiveChannel["BaseNode"]
        self._node_failure_send_channel, self._node_failure_receive_channel = node_failure_channels 

        self._app_command_send_channel: trio.MemorySendChannel[Dict[Any, Any]]
        self._app_command_receive_channel: trio.MemoryReceiveChannel[Dict[Any, Any]]
        self._app_command_send_channel, self._app_command_receive_channel = app_command_channels 

        self._ui_request_send_channel: trio.MemorySendChannel[str]
        self._ui_request_receive_channel: trio.MemoryReceiveChannel[str]
        self._ui_request_send_channel, self._ui_request_receive_channel = ui_request_channels 

        self._ui_response_send_channel: trio.MemorySendChannel[str]
        self._ui_response_receive_channel: trio.MemoryReceiveChannel[str]
        self._ui_response_send_channel, self._ui_response_receive_channel = ui_response_channels 

        self._tc_data_send_channel: trio.MemorySendChannel[Dict[Any, Any]]
        self._tc_data_receive_channel: trio.MemoryReceiveChannel[Dict[Any, Any]]
        self._tc_data_send_channel, self._tc_data_receive_channel = tc_data_channels 

        # COMMENT: Custom log handler and filter installation
        self._log_queue: Queue[logging.LogRecord | TestRunTerminalNode] = Queue()
        root_logger = logging.getLogger()
        ws_logger_handler = WebSocketLogHandler(self._log_queue)
        if root_logger.handlers:
            formatter = root_logger.handlers[0].formatter
            ws_logger_handler.setFormatter(formatter)
        ws_logger_handler.addFilter(TAGAppLoggerFilter())
        ws_logger_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(ws_logger_handler)

        # COMMENT: Application state manager initialization
        self._asm = ApplicationStateManager(
            self._tc_data_send_channel,  # type: ignore
            self._node_executor_send_channel,  # type: ignore
            self._ui_request_send_channel,  # type: ignore
            SampleTestProfile,
        )

        # COMMENT: Consumer initialization

        # COMMENT: Initialize communication modules
        self._ws_comm_module = WSCommModule(
            self._app_command_send_channel,  # type: ignore
            self._ui_response_send_channel,  # type: ignore
            self._asm,
        )
        self._node_executor: NodeExecutor = NodeExecutor(
            self._node_executor_receive_channel,  # type: ignore
            self._node_result_processor_send_channel,  # type: ignore
        )
        self._node_result_processor = NodeResultProcessor(
            self._node_result_processor_receive_channel,  # type: ignore
            self._node_failure_send_channel,  # type: ignore

        )

        self._node_failure_processor = NodeFailureProcessor(
            self._node_failure_receive_channel  # type: ignore
        )

        self._log_processor = LogProcessor(self._log_queue, self._ws_comm_module)
        self._ui_request_processor = UIRequestProcessor(
            self._ui_request_receive_channel,  # type: ignore
            self._ws_comm_module,
        )
        self._ui_response_processor = UIResponseProcessor(self._ui_response_receive_channel) # type: ignore
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

    async def retest(self, tc_id: str | None = None):
        # TODO: update the state of test case right away to avoid multiple command execution
        if self._asm.control_session is None:
            self._logger.error("Control session not established")
            raise Exception("Control session not established")
        if tc_id is not None and self._asm.control_session.panels[0].test_run is not None:
            await self._asm.control_session.panels[0].test_run.retest_failed_test_cases(tc_id)

    async def start(self):
        try:
            async with trio.open_nursery() as nursery:
                # NOTE: Each consumer can be considered as an attachment
                nursery.start_soon(self._ws_comm_module.start)
                nursery.start_soon(self._node_executor.start)
                nursery.start_soon(self._node_result_processor.start)
                nursery.start_soon(self._node_failure_processor.start)
                nursery.start_soon(self._log_processor.start)
                nursery.start_soon(self._ui_request_processor.start)
                nursery.start_soon(self._ui_response_processor.start)
                nursery.start_soon(self._tc_data_ws_processor.start)
                nursery.start_soon(self._app_command_processor.start)
        except Exception as e:
            self._logger.error(e)
            raise


# TODO: add a prompt upon test run termination
# TODO: handle prompt cancel action
# TODO: handle multi-user connection
# TODO: figure out product scan and test jig hardware config
# TODO: workflow configuration before App init phase

#TODO:
"""
Refactoring:
1. Configuration management
    - Externalize Configuration: Separate the configuration details (like channel sizes, logging
    settings, command mappings) from the code. Use a configuration file (JSON, YAML, etc) or 
    environment variables. This makes the system easier to adapt without modifying the code, 
    especially useful in different deployment environments.

2. Modularization
    - Break Down Large Classes: If classes like Application are doing too much, consider breaking 
    them down into smaller, more focused classes. For instance, the setup of channels and handlers 
    can be moved into their own setup functions or classes.
    - Component-Based Architecture: Organize the code into more distinct
    components or modules based on functionality (e.g., communication, node 
    management, UI handling)

3. Error Handling and Recovery
    - Advanced Error Management: Instead of just logging and raising exceptions,
    consider strategies for recovery, retires, or safe exits. Implementing these 
    within a dedicated error handling module or class could help centralize error
    management logic.
    - Graceful Shutdown: Ensure the application can shut down gracefully, handling 
    any clean-up tasks necessary to prevent data corruption or loss.

4. Dependency Injection
    - Implement Dependency Injection: For better testability and modularity, pass
    dependencies like channels or state managers through constructors or setters
    rather than creating them directly inside components. This makes it easier to
    swap out these dependencies, for example, during testing.

5. Enhance Asynchronous Management
    - Refactor Async Patterns: Review and possibly refactor how asynchronous tasks
    are managed to ensure that they are efficient and that resource locks or
    deadlocks are aboided. This might involve better utilization of Trio's capabilities
    or refactoring some synchronous blocks to be asynchronous.

6. Improving Logging
    - Centralize Logging Configuration: Instead of setting up logging in multiple 
    places or within application classes, consider having a centralized logging
    configuration that sets up all handlers and formats consistently across the 
    application.
"""