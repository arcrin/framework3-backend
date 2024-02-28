from node.sentinel_node import SentinelNode
from node.base_node import BaseNode
from typing import List
import asyncio


class NodeExecutor:
    def __init__(
        self,
        input_queue: asyncio.Queue[BaseNode],
        output_queue: asyncio.Queue[BaseNode],
        max_tasks: int = 100,
    ):
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._tasks: List[asyncio.Task[None]] = []
        self._max_tasks = max_tasks

    async def _execute_node(self, node: BaseNode):
        try:
          await node.execute()
          await self._output_queue.put(node)
        except Exception as e:
            # TODO: Handle the exception here
            print(f"An error occurred while executing node {node.name}: {e}")
            raise e


    async def process_queue(self):
        # TODO: this isn't executing test cases concurrently. I need to compare to the old implementation
        while True:
            node = await self._input_queue.get()
            if isinstance(node, SentinelNode):
                await self._output_queue.put(node)
                for task in self._tasks:
                    try:
                        await task
                    except Exception as e:
                        raise e
                return
            task = asyncio.create_task(self._execute_node(node))
            self._tasks.append(task)
            
            # If the queue is empty, wait for all tasks to complete before continuing
            if len(self._tasks) >= self._max_tasks:
                done, pending = await asyncio.wait(
                    self._tasks, return_when=asyncio.FIRST_COMPLETED
                )
                for task in done:
                    if task.exception() is not None:
                        # TODO: Handle the exception here, should I escalate it?
                        print(f"An error occurred while waiting for tasks to complete: {task.exception()}")
                        raise task.exception() # type: ignore
                self._tasks = list(pending)

    def start_processing(self):
        return asyncio.create_task(self.process_queue())
