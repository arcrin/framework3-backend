import trio

async def task1_func():
    print("task1 is running")
    await trio.sleep(1)
    raise ValueError("task1 failed with ValueError")
    # print("task1 is done")


async def task2_func():
    try:
        print("task2 is running")
        await trio.sleep(3)
        print("task2 is done")
    except trio.Cancelled:
        print("task2 Cancelled")


async def wrapper_level1():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(task1_func)

async def wrapper_level2():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(wrapper_level1)


async def parent():
    try:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(wrapper_level2)
            nursery.start_soon(task2_func)
    except* ValueError as excgroup:
        for exc in excgroup.exceptions:
            print(f"Caught the error: {exc}")



trio.run(parent)