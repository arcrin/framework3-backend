# type: ignore
from sample_profile.scripts import *
import trio
import inspect


async def task1():
    await trio.to_thread.run_sync(sync_task1)


async def task2():
    await trio.to_thread.run_sync(sync_task2)


async def task3():
    await trio.to_thread.run_sync(sync_task3)


async def task4():
    await trio.to_thread.run_sync(sync_task4)


async def task5():
    await trio.to_thread.run_sync(sync_task5)


async def task6():
    await trio.to_thread.run_sync(sync_task6)


async def task7():
    await trio.to_thread.run_sync(sync_task7)


jobs = [task1, task2, task4, task5, task6, task7]
# jobs = [task_func3, task_func5, task_func7]


async def producer(send_channel):
    async with send_channel:
        for job in jobs:
            await send_channel.send(job)
            print(f"sent {job!r}")


async def consumer(receive_channel):
    async with trio.open_nursery() as nursery:
        async with receive_channel:
            async for job in receive_channel:
                print(f"got value {job!r}")
                if inspect.iscoroutinefunction(job):
                    nursery.start_soon(job)
                else:
                    await trio.to_thread.run_sync(job)


async def main():
    start_time = trio.current_time()
    async with trio.open_nursery() as nursery:
        send_channel, receive_channel = trio.open_memory_channel(10)
        nursery.start_soon(producer, send_channel)
        nursery.start_soon(consumer, receive_channel)
    end_time = trio.current_time()
    print(f"Total time taken: {end_time - start_time}")


async def wrapper():
    async with trio.open_nursery() as nursery:
        # nursery.start_soon(task_func1)
        # nursery.start_soon(task_func2)

        # order of tasks matter here. If await is sequenced earlier in the nursery, it will
        # block until it
        # await trio.to_thread.run_sync(task_func3)   

        # Nursery only exits when all tasks inside it are done. This doesn't help with blocking functions
        # async with trio.open_nursery() as inner_nursery:
        #     await trio.to_thread.run_sync(task_func3)

        nursery.start_soon(task3)

        # nursery.start_soon(task_func4)
        nursery.start_soon(task_func5)
        # nursery.start_soon(task_func6)
        nursery.start_soon(task_func7)
        

# async def main():
#     start_time = trio.current_time()
#     async with trio.open_nursery() as nursery:
#         nursery.start_soon(wrapper)
#     end_time = trio.current_time()
#     print(f"Total time taken: {end_time - start_time}")


trio.run(main)


# Avoid having await keyword inside the main nursery.
# Wrap await trio.to_thread.run_sync(sync_func) inside a coroutine

# The only way to run a synchronous function in parallel inside a nursery is to 
# wrap in inside a coroutine
