#type: ignore
import trio
from trio_websocket import serve_websocket, ConnectionClosed
import sys

async def echo_server(request):
    ws = await request.accept()
    send_channel, receive_channel = trio.open_memory_channel(0)

    async def get_input():
        while True:
            try:
                message = await trio.to_thread.run_sync(input, "Enter a message: ")
                await send_channel.send(message)
            except trio.BrokenResourceError:
                print("Channel closed")

    async def echo_messages():
        async with receive_channel:
            async for message in receive_channel:
                try:
                    await ws.send_message(message)
                except ConnectionClosed:
                    pass

    async with trio.open_nursery() as nursery:
        nursery.start_soon(get_input)
        nursery.start_soon(echo_messages)

async def main():
    await serve_websocket(echo_server, '127.0.0.1', 8000, ssl_context=None)

trio.run(main)