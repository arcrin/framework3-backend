# type: ignore
import time
import trio

async def main():
  event = trio.Event()

  async with trio.open_nursery() as nursery:
    # nursery.start_soon(waiter, 1, event)
    # nursery.start_soon(waiter, 2, event)
    await trio.to_thread.run_sync(sync_task)

    await trio.sleep(4)

    event.set()
    print("Event is set")

async def waiter(id, event):
  print(f"Task {id} waiting for event")
  await event.wait()
  print(f"Task {id} got event")

def sync_task():
  count = 0
  while True:
    print("Sync task running")
    if count == 3:
      print("Wait fro async task")
      trio.from_thread.run(sync_task_wrapper)
    time.sleep(1)
    count += 1

async def sync_task_wrapper():
  print("Start async task")
  await trio.sleep(3)

trio.run(main)
