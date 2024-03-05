# type: ignore
import trio
from itertools import count

PORT = 12345

CONNECTION_COUNTER = count()

async def echo_server(server_stream):
  ident = next(CONNECTION_COUNTER)
  print(f"echo_server {ident}: started")
  try:
    async for data in server_stream:
      print(f"echo_server {ident}: received data {data!r}")
      await server_stream.send_all(data)
    print(f"echo_server {ident}: connection closed")

  except Exception as exc:
    print(f"echo_server {ident}: crashed: {exc!r}")

async def main():
  await trio.serve_tcp(echo_server, PORT)

trio.run(main)