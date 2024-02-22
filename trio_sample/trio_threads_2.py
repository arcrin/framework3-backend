from sample_profile.scripts import task_func3, task_func7
import trio

async def main():
  try:
    with trio.move_on_after(11):
      async with trio.open_nursery() as nursery:
        nursery.start_soon(task2)
        nursery.start_soon(task1)
  except* ValueError as excgroup:
    for exc in excgroup.exceptions:
      print(f"ValueError: {exc}") 

async def task1():
  async with trio.open_nursery() as nursery:
    await trio.to_thread.run_sync(task_func3, 20)

async def task2():
  try:
    async with trio.open_nursery() as nursery:
      nursery.start_soon(task_func7)
  except trio.Cancelled:
    print("task2 cancelled")

trio.run(main)