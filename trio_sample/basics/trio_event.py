# type: ignore
import trio

async def main():
  event = trio.Event()

  async with trio.open_nursery() as nursery:
    nursery.start_soon(waiter, 1, event)
    nursery.start_soon(waiter, 2, event)

    await trio.sleep(2)

    event.set()
    print("Event is set")

async def waiter(id, event):
  print(f"Task {id} waiting for event")
  await event.wait()
  print(f"Task {id} got event")

trio.run(main)
