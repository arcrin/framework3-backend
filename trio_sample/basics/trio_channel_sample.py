#type: ignore

import trio

async def main():
  async with trio.open_nursery() as nursery:
    send_channel, receive_channel = trio.open_memory_channel(0)
    nursery.start_soon(producer, send_channel)
    nursery.start_soon(consumer, receive_channel)


async def producer(send_channel):
  try:
    async with send_channel:
      for i in range(5):
        await send_channel.send(i)
        print(f"sent {i!r}")
  except trio.BrokenResourceError:
    print("consumer channel closed")


async def consumer(receive_channel):
  # async with receive_channel:
  async for value in receive_channel:
    await trio.sleep(1)
    if value == 3:
      await receive_channel.aclose()
      break
    print(f"got value {value!r}")

trio.run(main)