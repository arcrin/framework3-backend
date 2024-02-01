# type: ignore
from typing import Callable, Any, TypeVar, Coroutine, Dict, List
import matplotlib.pyplot as plt
import os
import asyncio
import functools
import time

task_timing: List[Dict[str, Any]] = []

async def delay(delay_seconds: int) -> int:
  print(f"sleeping for {delay_seconds} seconds")
  await asyncio.sleep(delay_seconds)
  print(f"finished sleeping for {delay_seconds} seconds")
  return delay_seconds

T = TypeVar("T")

def async_timed(node_name: str):
  def wrapper(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
    @functools.wraps(func)
    async def wrapped(*args: Any, **kwargs: Any) -> Any:
      global task_timing
      start = time.time()
      try:
        return await func(*args, **kwargs)
      finally:
        end = time.time()
        total = end - start 
        print(f"finished {func} in {total:.4f} seconds\n")
        task_timing.append({"task": node_name, 
                            "start_time": start,
                            "end_time": end})
    return wrapped
  return wrapper


def plot_task_timing():
    fig, ax = plt.subplots()

    for i, task in enumerate(task_timing):
        start_time_seconds = task["start_time"] - task_timing[0]["start_time"]
        end_time_seconds = task["end_time"] - task_timing[0]["start_time"]
        execution_time_seconds = end_time_seconds - start_time_seconds
        ax.barh(i, execution_time_seconds, left=start_time_seconds)

    ax.set_yticks(range(len(task_timing)))
    ax.set_yticklabels([task["task"] for task in task_timing])
    ax.set_xlabel("Seconds")
    ax.set_title("Function Execution Timeline")

    plt.savefig('function_execution_timeline.pdf')
    os.startfile('function_execution_timeline.pdf')