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