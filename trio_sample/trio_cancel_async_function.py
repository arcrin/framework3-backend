import trio

async def task1():
    try:
        while True:
            print("task1 running")
            await trio.sleep(1)
    except trio.Cancelled:
        print("task1 cancelled")

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(task1)
        await trio.sleep(3)
        nursery.cancel_scope.cancel()

trio.run(main)