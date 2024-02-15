#type: ignore
import trio
import random

async def producer(name, send_channel):
  for i in range(5):
    item = f"{name} - {i}"
    print(f"{name} produced item: {item}")
    await send_channel.send(item)
    await trio.sleep(random.uniform(1.0, 0.5))


async def consumer(name, receive_channel):
  async for item in receive_channel:
    print(f"{name} consumed item: {item}")
    await trio.sleep(random.uniform(1.0, 0.5))


async def main():
  send_channel1, receive_channel1 = trio.open_memory_channel(0)
  send_channel2, receive_channel2 = trio.open_memory_channel(0)

  async with trio.open_nursery() as nursery:
    nursery.start_soon(producer, "Producer 1", send_channel1)
    nursery.start_soon(producer, "Producer 2", send_channel2)

    async with trio.open_nursery() as nursery:
      nursery.start_soon(consumer, "Consumer 1", receive_channel1)
      nursery.start_soon(consumer, "Consumer 2", receive_channel2)

trio.run(main)