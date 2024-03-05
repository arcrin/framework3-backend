#type: ignore
import trio

async def child_task(nursery_id, task_id):
  print(f"Child task {task_id} in nursery {nursery_id} started")
  await trio.sleep(1)
  print(f"Child task {task_id} in nursery {nursery_id} finished")

async def main():
  async with trio.open_nursery() as nursery:
    for i in range(3):
      async with trio.open_nursery() as child_nursery:
        for j in range(3):
          child_nursery.start_soon(child_task, i, j)

trio.run(main)