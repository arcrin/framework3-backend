#type: ignore
import trio


async def broken1():
  try:
    d = {}
    return d["key"]
  except KeyError as exc:
    print(f"KeyError: {exc}")

async def broken2():
  try:
    seq = range(10)
    return seq[20]
  except IndexError as exc:
    print(f"IndexError: {exc}")

async def task():
  try:
    await trio.sleep(3)
    print("task done")
  except trio.Cancelled:
    print("task cancelled")

async def parent():
  try:
    async with trio.open_nursery() as nursery:
      nursery.start_soon(broken1)
      nursery.start_soon(broken2)
      nursery.start_soon(task)
  except* KeyError as excgroup:
    for exc in excgroup.exceptions:
      print(f"KeyError: {exc}") 
  except* IndexError as excgroup: 
    for exc in excgroup.exceptions:
      print(f"IndexError: {exc}")

  
trio.run(parent)