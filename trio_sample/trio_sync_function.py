# type: ignore
import trio

async def download_file(url):
    # Simulate file download (assuming this is asynchronous)
    await trio.sleep(1)
    print(f"Downloaded file: {url}")

def sync_function(x):
    # Simulate a blocking operation
    import time
    time.sleep(2)
    return x * 2

async def main():
    async with trio.open_nursery() as nursery:
        # Start a task to download a file asynchronously
        nursery.start_soon(download_file, "https://example.com/file.txt")

        # Use trio.to_thread.run_sync for a simple calculation
        result = trio.to_thread.run_sync(sync_function, 5)
        print(f"Result from sync function (non-blocking): {result}")

        # Wait for the file download task to finish

if __name__ == "__main__":
    trio.run(main)



