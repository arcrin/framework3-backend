#type: ignore
from queue import Queue
import logging
import trio


class WebSocketLogHandler(logging.Handler):
    def __init__(self, log_queue: Queue[logging.LogRecord]):
        super().__init__()
        self._log_queue = log_queue 
        

    def emit(self, record) -> None:
        self._log_queue.put(record)