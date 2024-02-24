import asyncio

async def task1_func():
    print("task1 is running")
    await asyncio.sleep(1)
    raise ValueError("task1 failed with ValueError")
    # print("task1 is done")

async def task2_func():
    print("task2 is running")
    await asyncio.sleep(3)
    print("task2 is done")

async def wrapper_level1():
    try:
        asyncio.create_task(task1_func())
    except ValueError:
        raise

async def wrapper_level2():
    try:
        asyncio.create_task(wrapper_level1())
    except ValueError:
        raise

async def parent():
    task1 = asyncio.create_task(task1_func())
    task2 = asyncio.create_task(task2_func())
    try:
        await asyncio.gather(task1, task2, return_exceptions=False)
    except ValueError as e:
        print(f"Caught the error: {e}") 

asyncio.run(parent())