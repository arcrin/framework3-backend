# type: ignore
from sample_profile.scripts import *
import trio
import inspect


async def task1():
    async with trio.open_nursery() as nursery:
        await task_func1()

async def task2():
    async with trio.open_nursery() as nursery:
        await task_func2()

async def task3():
    async with trio.open_nursery() as nursery:
        await trio.to_thread.run_sync(task_func3)

async def task4():
    async with trio.open_nursery() as nursery:
        await task_func4()

async def task5():
    async with trio.open_nursery() as nursery:
        await task_func5()

async def task6():
    async with trio.open_nursery() as nursery:
        await task_func6()

async def task7():
    async with trio.open_nursery() as nursery:
        await task_func7()

jobs = [task1, task2, task3, task4, task5, task6, task7]


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
                nursery.start_soon(job)

async def main():
    start_time = trio.current_time()
    async with trio.open_nursery() as nursery:
        send_channel, receive_channel = trio.open_memory_channel(10)
        nursery.start_soon(producer, send_channel)
        nursery.start_soon(consumer, receive_channel)
    end_time = trio.current_time()
    print(f"Total time taken: {end_time - start_time}")

trio.run(main)
