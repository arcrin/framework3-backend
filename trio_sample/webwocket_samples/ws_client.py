#type: ignore
#type: ignore
from trio_websocket import open_websocket_url
import trio

async def main():
    try:
        async with open_websocket_url('ws://localhost:8000') as ws:
            while True:
                message = await ws.get_message()
                print(message)
    except OSError as ose:
        print(f"Connection attempt failed: {ose}")

trio.run(main)

