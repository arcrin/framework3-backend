# type: ignore
import trio

async def loopy_child(number, lock):
  while True:
    async with lock:
      print(f"Child {number} has the lock!")
      await trio.sleep(1)

async def main():
  async with trio.open_nursery() as nursery:
    lock = trio.Lock()
    nursery.start_soon(loopy_child, 1, lock)
    nursery.start_soon(loopy_child, 2, lock)  

trio.run(main)