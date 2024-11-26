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

"""
The Application class is the central orchetrator of your system, responsible for initializing and running all components,
handling communication channels, and managing the application's lifecycle. 


Strengths
1. Centralized Initialization
    - All components and dependencies are initialized in one place, providing a clear overview of the system's setup

2. Seamless Integration of Producer-Consumer Pattern:
    - The Application class orchestrates the interaction between different producers and consumers effectively, leveraging
    Trio's asynchronous capabilities.

3. Modular Design:
    - Different components, such as Node Executor, LogProcessor, and UIRequestProcessor, are encapsulated, adhering to the 
    Single Responsibility Principle (SRP).

4. Channel-Based Communication
    - The use of Trio memory channels ensures efficient and thread-safe communication between components.

5. Dynamic Command Mapping:
    - The _command_mapping dictionary allows for extensible command handling, making it easy to add new commands.

6. Clear Logging Setup:
    - The logging mechanism, with custom handlers and filters, ensures that logs are appropriately formatted and routed.

7. Error Isolation:
    - Components are started in separate nursery tasks, isolating errors and ensuring that the failure of one component 
    doesn't crash the entire application.


Potential Improvements
1. Dependency Injection
    - The Application class directly instantiates components, coupling it tightly to specific implementations.

    - Solution:
        - Use Dependency Injection (DI) to decouple the initialization logic and make the class more testable modular.
        - For instance, pass pre-configured components or a DI container into the Application constructor

2. Simplify Channel Initialization
    - The current method of unpacking and assigning channels is repetitive.
    - Solution
        - Create a helper method or object to encapsulate channel initialization:
        
            def create_channel_pair():
                send_channel, receive_channel = trio.open_memory_channel(0)
                return send_channel, receive_channel

            self._node_executor_channels = create_channel_pair()
            self._node_result_processor_channels = create_channel_pair()
            
3. Handle Command Failures Gracefully
    - The start_test_run and retest methods raise exceptions that could disrupt the application.
    - Solution:
        - Handle errors more gracefully, such as logging them or notifying the user, instead of stopping the application:

            async def start_test_run(self):
                if not self._asm.control_session:
                    self._logger.error("Control session not established")
                    return
                try:
                    for panel in self._asm.control_session.panels:
                        await panel.add_test_run()
                        await panel.test_run.load_test_case()
                except Exception as e:
                    self._logger.error(f"Error during test run: {e}")
            
            
4. Enhance Modularity
    - The Application class contains both high-level orchestration and some low-level details, such as command mapping and direct access to channels.
    - Solution:
        - Delegate command handling to a CommandHandler class and abstract channel management into a separate utility.

        
5. Add Graceful Shutdown
    - Currently, there is not explicit shutdown logic for stopping components or cleaning up resources.
    - Solution:
        - Add a stop method to shut down all consumers and close channels gracefully:

            async def stop(self):
                self._logger.info("Shutting down application...")
                await self._ws_comm_module.stop()
                await self._node_executor.stop()
                # Add similar stop methods for other components

6. Dynamic Component Loading
    - Hardcoding all components in the Application class limits flexibility
    - Solution:
        - Dynamically load components from a configuration or registry, making it easier  to add or remove features. (Another DI?)
        

Scalability Considerations
1. Error Propagation:
    - Ensure that errors in one component do not propagate to others. Currently, the exception handling in start appears robust but could benefit from more 
    granular control.

2. Monitoring and Metrics:
    - Add hooks or instrumentation to monitor the health and performance of each component, especially in production environments.

3. Dynamic Command Registration:
    - Allow commands to be registered dynamically rather than hardcoding them in _command_mapping.

    

Refactored Initialization Example

    class Application:
        def __init__(self, dependencies):
            self._logger = logging.getLogger("Application")
            self._dependencies = dependencies  # DI container or pre-configured components
            self._initialize_components()

        def _initialize_components(self):
            # Example: Retrieve components from dependencies
            self._node_executor = self._dependencies.get("NodeExecutor")
            self._node_result_processor = self._dependencies.get("NodeResultProcessor")
            self._log_processor = self._dependencies.get("LogProcessor")
            # ... Load other components dynamically

Final Thoughts

The Application class is well-structured and provides a clear entry point for managing the entire system. Implementing some of the suggested improvements will
make it more robust, modular, and scalable.
"""