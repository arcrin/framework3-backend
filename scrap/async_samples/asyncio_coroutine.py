import asyncio


async def f():
    try:
        while True: await asyncio.sleep(0)
    except asyncio.CancelledError:
        print('I was cancelled!')
    else:
        return 111

