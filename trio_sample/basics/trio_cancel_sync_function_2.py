# type: ignore
import time
import trio


def long_running_task(duration, cancel_flag):
    print("Starting long-running task")
    start_time = time.time()
    while time.time() - start_time < duration:
        print("Synchronous function working...")
        time.sleep(1)  # Simulates work by sleeping
        if cancel_flag.is_set():
            print("Task was cancelled!")
            return
    print("Long-running task completed!")


async def async_wrapper(sync_func, duration, cancel_flag):
    await trio.to_thread.run_sync(sync_func, duration, cancel_flag)


async def async_task():
    await trio.sleep(3)
    raise ValueError("async_task failed with ValueError")


async def main():
    cancel_flag = trio.Event()
    try:
        async with trio.open_nursery(strict_exception_groups=False) as nursery:
            # nursery.start_soon(async_wrapper, long_running_task, 10, cancel_flag)
            await trio.to_thread.run_sync(long_running_task, 10, cancel_flag)
            nursery.start_soon(async_task)
    except ValueError as exc:
        print(f"ValueError: {exc}")
        cancel_flag.set()
        
trio.run(main)
