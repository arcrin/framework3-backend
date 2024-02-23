# type: ignore
import trio


def sync_function():
  trio.sleep(1)

trio.run(main)
