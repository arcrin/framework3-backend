import trio

async def foo1():
  print("starting...")
  with trio.move_on_after(5):
    with trio.move_on_after(10):
      await trio.sleep(20)
      print("sleep finished without error")
    print("move_on_after(10) finished without error")
  print("move_on_after(5) finished without error")

async def foo2():
  with trio.move_on_after(5):
    try:
      await task1(100)
      print("sleep finished without error")
    finally:
      await task1(50)
      print("finally block ran")

async def task1(timeout:int):
  try:
    print(f"task started: {timeout}")
    await trio.sleep(timeout)
  except trio.Cancelled:
    print(f"task {timeout} cancelled")

async def task2():
  while True:
    deadline = trio.current_effective_deadline()
    print(f"Effective deadline: {deadline: .2f}")
    await trio.sleep(1)

async def main():
  print(trio.current_time())
  with trio.move_on_after(2):
    with trio.move_on_after(5):
      with trio.move_on_after(5):
        with trio.move_on_after(5):
          with trio.move_on_after(5):
            await task2()


trio.run(main)