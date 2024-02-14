# type: ignore
import sys
import trio

PORT = 12345

async def sender(client_stream):
  print("sender: started!")
  while True:
    data = b"async can be confusing, but I believe in you!"
    print(f"sender: sending {data!r}")
    await client_stream.send_all(data)
    await trio.sleep(1)

async def receiver(client_stream):
  print("receiver: started!")
  # async for data in client_stream:
  data = await client_stream.receive_some(16)
  print(f"receiver: got data {data!r}")
  print("receiver: connection closed")
  sys.exit()


async def parent():
  print(f"parent: connection to 127.0.0.1: {PORT}")
  client_stream = await trio.open_tcp_stream("127.0.0.1", PORT)
  async with client_stream:
    async with trio.open_nursery() as nursery:
      print("parent: spawning sender...")
      nursery.start_soon(sender, client_stream)
      print("parent: spawning receiver...")
      nursery.start_soon(receiver, client_stream)


trio.run(parent)
