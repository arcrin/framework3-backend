# type: ignore
import trio

async def task1():
  try:
    await trio.sleep(5)
  except trio.Cancelled:
    print("task1 cancelled")

async def task2():
  try:
    await trio.sleep(10)
  except trio.Cancelled:
    print("task2 cancelled")
    
async def main():
  with trio.move_on_after(3):
    async with trio.open_nursery() as nursery:
      nursery.start_soon(task1)
      nursery.start_soon(task2)

trio.run(main)