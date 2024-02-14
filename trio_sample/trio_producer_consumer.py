# type: ignore
import trio
import random

async def producer(name, output_channel):
  for i in range(5):
    item = f"{name} - {i}"
    print(f"{name} produced item: {item}")
    await output_channel.send(item)
    await trio.sleep(random.uniform(1.0, 0.5))

async def consumer(name, input_channel):
  while True:
    item = await input_channel.receive()
    print(f"{name} consumed item: {item}")
    await trio.sleep(random.uniform(1.0, 0.5))

async def main():
  output_channel, input_channel = trio.open_memory_channel(5)

  async with trio.open_nursery() as nursery:
    for i in range(3):
      nursery.start_soon(producer, f"Producer {i}", output_channel)

  async with trio.open_nursery() as nursery:
    for i in range(2):
      nursery.start_soon(consumer, f"Consumer {i}", input_channel)

trio.run(main)
