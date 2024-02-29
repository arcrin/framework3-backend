from application import Application
from util.async_timing import plot_task_timing
import trio
import logging


class TAGAppLoggerFilter(logging.Filter):
    def filter(self, record: logging.LogRecord): 
        return not (record.name.startswith("matplotlib") or 
                    record.name.startswith("PIL") or
                    record.name.startswith("asyncio"))

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

app = Application()
trio.run(app.start)
plot_task_timing()