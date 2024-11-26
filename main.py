from typing import TYPE_CHECKING, Dict, Any
from _Application._Application import Application
# from util.async_timing import plot_task_timing
from util.log_filter import TAGAppLoggerFilter
if TYPE_CHECKING:
    from _Node._BaseNode import BaseNode
import trio
import logging

MAX_CHANNEL_SIZE = 50
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")


file_handler = logging.FileHandler("tag_application.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
file_handler.addFilter(TAGAppLoggerFilter())

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
console_handler.addFilter(TAGAppLoggerFilter())


logger.addHandler(file_handler)
logger.addHandler(console_handler)

node_executor_send_channel: trio.MemorySendChannel["BaseNode"]
node_executor_receive_channel: trio.MemoryReceiveChannel["BaseNode"]
node_executor_send_channel, node_executor_receive_channel = trio.open_memory_channel(MAX_CHANNEL_SIZE)

node_result_processor_send_channel: trio.MemorySendChannel["BaseNode"]
node_result_processor_receive_channel: trio.MemoryReceiveChannel["BaseNode"]
node_result_processor_send_channel, node_result_processor_receive_channel = trio.open_memory_channel(MAX_CHANNEL_SIZE)

node_failure_send_channel: trio.MemorySendChannel["BaseNode"]
node_failure_receive_channel: trio.MemoryReceiveChannel["BaseNode"]
node_failure_send_channel, node_failure_receive_channel = trio.open_memory_channel(MAX_CHANNEL_SIZE)

app_command_send_channel: trio.MemorySendChannel[Dict[Any, Any]]
app_command_receive_channel: trio.MemoryReceiveChannel[Dict[Any, Any]]
app_command_send_channel, app_command_receive_channel = trio.open_memory_channel(MAX_CHANNEL_SIZE)

ui_request_send_channel: trio.MemorySendChannel[str]
ui_request_receive_channel: trio.MemoryReceiveChannel[str]
ui_request_send_channel, ui_request_receive_channel = trio.open_memory_channel(MAX_CHANNEL_SIZE)

ui_response_send_channel: trio.MemorySendChannel[str]
ui_response_receive_channel: trio.MemoryReceiveChannel[str]
ui_response_send_channel, ui_response_receive_channel = trio.open_memory_channel(MAX_CHANNEL_SIZE)

tc_data_send_channel: trio.MemorySendChannel[Dict[Any, Any]]
tc_data_receive_channel: trio.MemoryReceiveChannel[Dict[Any, Any]]
tc_data_send_channel, tc_data_receive_channel = trio.open_memory_channel(MAX_CHANNEL_SIZE)

app = Application(
    (node_executor_send_channel, node_executor_receive_channel),
    (node_result_processor_send_channel, node_result_processor_receive_channel),
    (node_failure_send_channel, node_failure_receive_channel),
    (app_command_send_channel, app_command_receive_channel),
    (ui_request_send_channel, ui_request_receive_channel),
    (ui_response_send_channel, ui_response_receive_channel),
    (tc_data_send_channel, tc_data_receive_channel),    
)
trio.run(app.start)
# plot_task_timing()


"""
The main.py file serves as the entry point for your application, where channels are set up, logging is configured, and the application is initialized
and executed. Here's a detailed analysis:

Key Observation
1. Logging Setup:
    - Logging is configured to log to both a file and the console.
    - Filters are applied (TagAppLoggerFilter) to control what gets logged, ensuring relevant output.

2. Channel Initialization:
    - Multiple trio.MemoryChannel instances are created to facilitate communication between components of the application.

3. Application Initialization:
    - The Application class is instantiated with the pre-configured channels and starts with trio.run()

4. Task Timing (Commented Out):
    - A utility (plot_task_timing) for task timing analysis is included but commented out. This could be useful for debugging or performance monitoring.
    

Strengths
1. Separation of Concerns:
    - main.py focuses on setting up the environment and launching the application, while the core logic resides in the Application class and other components

2. Flexible Channel Sizes:
    - The MAX_CHANNEL_SIZE parameter provides a centralized way to control buffer sizes for all channels.

3. Clean Initialization:
    - The Application class receives all necessary channels during initialization, keeping the setup organized.

4. Logging:
    - Dual logging (console and file) ensures easy debugging during development and aceess to historical logs for troubleshooting.


Areas for Improvement
1. Reduce Channel Boilerplate
    - The repeated creation of channels is verbose and error-prone.
    - Solution: Use a helper function to streamline channel creation.

        def create_channel():
            return trio.open_memory_channel(MAX_CHANNEL_SIZE)

        node_executor_send_channel, node_executor_receive_channel = create_channel() 

2. Consider Dependency Injection for Channels
    - Instead of creating channels in main.py, you could manage them in a dependency injection (DI) container and pass the container to Application.
    - Benefit:
        - Reduces clutter in main.py and allows centralized dependency management.

        Example:

            from injector import Injector, Module

            class AppModule(Module):
                def configure(self, binder):
                    binder.bind(trio.MemorySendChannel, to=create_channel())
                    binder.bind(trio.MemoryReceiveChannel, to=create_channel())


3. Add Error Handling
    - Currently, there is no top-level error handling for trio.run(app.start)
    - Solution:
        - Wrap the application execution in a try-except block catch and log any unhandled exceptions:

            try:
                trio.run(app.start)
            except Exception as e:
                logger.error(f"Unhandled exception: {e}")

            
4. Improve Logging for Production Use
    - Consider rotating logs for long-running systems.
    - Solution:
        - Use logging.handlers.RotatingFileHandler to manage log file size and retention:

            from logging.handlers import RotatingFilehandler

            file_handler = RotatingFileHandler("tag_application.log", maxByte=10*1024*1024, backCount=5)


5. Make Task Timing a Configurable Option
    - The plot_task_timing() utility is commented out but could be useful for debugging.
    - Solution:
        - Add a command-line flag to enable task timing:

            import argparse

            parser = argparse.ArgumentParser()
            parser.add_argument("--timing", action="store_true", help="Enable task timing")
            args = parser.parse_args()

            if args.timing:
                plot_task_timing()
                
    
6. Configurable Parameters
    - The MAX_CHANNEL_SIZE and other settings are hardcoded.
    - Solution:
        - Use a configuration file or enviroment variables to allow dynamic parameter adjustments:

            import os

            MAX_CHANNEL_SIZE = int(os.getenv("MAX_CHANNEL_SIZE", 50))


Refactored Example:

        import trio
        import logging
        from _Application._Application import Application
        from util.log_filter import TAGAppLoggerFilter

        MAX_CHANNEL_SIZE = 50

        def setup_logger():
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter("%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")

            file_handler = logging.FileHandler("tag_application.log")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            file_handler.addFilter(TAGAppLoggerFilter())

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.DEBUG)
            console_handler.addFilter(TAGAppLoggerFilter())

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        def create_channel():
            return trio.open_memory_channel(MAX_CHANNEL_SIZE)

        def main():
            setup_logger()
            logger = logging.getLogger("Main")

            # Create channels
            node_executor_channels = create_channel()
            node_result_processor_channels = create_channel()
            node_failure_channels = create_channel()
            app_command_channels = create_channel()
            ui_request_channels = create_channel()
            ui_response_channels = create_channel()
            tc_data_channels = create_channel()

            # Initialize application
            app = Application(
                node_executor_channels,
                node_result_processor_channels,
                node_failure_channels,
                app_command_channels,
                ui_request_channels,
                ui_response_channels,
                tc_data_channels,    
            )

            # Start application
            try:
                trio.run(app.start)
            except Exception as e:
                logger.error(f"Unhandled exception: {e}")

        if __name__ == "__main__":
            main()


Final Thoughts

The main.py is well-structured as a launch scrip, by with tweaks like better error handling, reduced boilerplate, and configurable parameters, it could become even more 
robust and maintainable.
"""