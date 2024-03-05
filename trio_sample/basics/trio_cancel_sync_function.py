# type: ignore
import trio
import time
from sample_profile.scripts import task_func7, task_func4

def synchronous_function():
  count = 0
  while True:
    time.sleep(1)
    count += 1
    if count == 5:
      raise ValueError("synchronous_function failed with ValueError")
    print("synchronous_function running")

async def main():
  try:
    async with trio.open_nursery() as nursery:  
      await trio.to_thread.run_sync(synchronous_function)
      nursery.start_soon(task_func7)
  except* ValueError as excgroup:
    for exc in excgroup.exceptions:
      print(f"ValueError: {exc}")

trio.run(main)