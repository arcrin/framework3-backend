# type: ignore
import trio


async def horse1():
  await trio.sleep(3)
  return "horse1"

async def horse2():
  await trio.sleep(2)
  return "horse2"

async def horse3():
  await trio.sleep(1)
  return "horse3"

race_participants = [
  horse1,
  horse2,
  horse3
]
async def race(*async_fns):
  if not async_fns:
    raise ValueError("must pass at least one argument")

  winner = None

  async def jockey(async_fn, cancel_scope):
    nonlocal winner
    winner = await async_fn()
    cancel_scope.cancel()

  async with trio.open_nursery() as nursery:
    for async_fn in async_fns:
      nursery.start_soon(jockey, async_fn, nursery.cancel_scope)

  print(winner)

trio.run(race, *race_participants)