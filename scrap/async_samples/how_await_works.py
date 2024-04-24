import trio


def fibonacci(n):
    if n <= 0:
        return "Invalid input"
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


async def foo():
    print("Running foo")
    print(f"foo fibonacci: {fibonacci(35)}")
    await trio.sleep(3)
    print("foo done")

async def foo1():
    print("Running foo1")
    print(f"foo1 fibonacci: {fibonacci(30)}")
    await trio.sleep(2)
    print("foo1 done")


async def foo3():
    await foo()

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(foo1)
        nursery.start_soon(foo3)

if __name__ == "__main__":
    trio.run(main)