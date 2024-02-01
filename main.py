from application import Application
from util.async_timing import plot_task_timing
import asyncio

app = Application()
asyncio.run(app.start())
plot_task_timing()