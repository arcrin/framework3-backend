import trio
import time


def fib(n: int) -> int:
    if n <= 1:
        return n
    else:
        return (fib(n-1) + fib(n-2))

async def async_task1():
    print("Start async task1")
    await trio.sleep(1)
    return 1

async def async_task2():
    print("Start async task2")
    await trio.sleep(2)
    return 2

async def async_task3(task1_parameter: int | None = None, task2_parameter: int | None=None):
    if task1_parameter is None or task2_parameter is None:
        raise ValueError("task1_parameter and task2_parameter are required")
    print("Start async task3")
    await trio.sleep(3)
    return task1_parameter + task2_parameter

async def async_task4():
    print("Start async task4")
    await trio.sleep(4)
    return True

async def async_task5():
    print("Start async task5")
    await trio.sleep(5)
    return True


async def async_task6():
    print("Start async task6")
    await trio.sleep(6)
    return True


async def async_task7():
    print("Start async task7")
    await trio.sleep(7)
    return True


def sync_task1():
    print("Start sync task1")
    time.sleep(1)
    return 1

def sync_task2():
    print("Start sync task2")
    time.sleep(2)
    return 2

def sync_task3(task1_parameter: int | None = None, task2_parameter: int | None=None):
    if task1_parameter is None or task2_parameter is None:
        raise ValueError("task1_parameter and task2_parameter are required")
    print("Start sync task3")
    time.sleep(3)
    return task1_parameter + task2_parameter

def sync_task4():
    print("Start sync task4")
    time.sleep(4)
    return True

def sync_task5():
    print("Start sync task5")
    time.sleep(5)
    return True

def sync_task6():
    print("Start sync task6")
    time.sleep(6)
    return True

def sync_task7():
    print("Start sync task7")
    time.sleep(7)
    return True