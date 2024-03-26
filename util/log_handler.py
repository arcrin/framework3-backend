from queue import Queue
from _Node._TerminalNode import TerminalNode
import logging 


class WebSocketLogHandler(logging.Handler):
    def __init__(self, log_queue: Queue[logging.LogRecord | TerminalNode]):
        super().__init__()
        self._log_queue = log_queue 
        

    def emit(self, record) -> None:
        self._log_queue.put(record)