# type: ignore
import time
import trio

async def broken_double_sleep(x):
  print("Going to sleep")
  start_time = time.perf_counter()

  await trio.sleep(2 * x)

  sleep_time = time.perf_counter() - start_time
  print(f"woke up after {sleep_time:.2f} seconds")
  return 15

result = trio.run(broken_double_sleep, 3)
print(result)
