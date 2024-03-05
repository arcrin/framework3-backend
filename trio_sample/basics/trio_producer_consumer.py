# type: ignore
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
  send_channel, receive_channel = trio.open_memory_channel(0)

  async with trio.open_nursery() as nursery:
    for i in range(3):
      nursery.start_soon(producer, f"Producer {i}", send_channel)

  async with trio.open_nursery() as nursery:
    for i in range(2):
      nursery.start_soon(consumer, f"Consumer {i}", receive_channel)

trio.run(main)
