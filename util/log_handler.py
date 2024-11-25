# type: ignore
from queue import Queue
from _Node._TestRunTerminalNode import TestRunTerminalNode
import logging 


class WebSocketLogHandler(logging.Handler):
    def __init__(self, log_queue: Queue[logging.LogRecord | TestRunTerminalNode]):
        super().__init__()
        self._log_queue = log_queue 
        

    def emit(self, record) -> None:
        self._log_queue.put(record)