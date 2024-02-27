from node.base_node import BaseNode
from typing import Callable, Any
from util.async_timing import async_timed
import inspect
import trio


class TCNode(BaseNode):
    """
    A wrapper around test cases.
    """

    def __init__(self, callable_object: Callable[..., Any], name: str | None=None) -> None:
        super().__init__(callable_object.__name__ if name is None else name)
        self._callable_object = callable_object
        self._result: Any = None
        self.execute = async_timed(self.name)(self.execute)

    @property
    def result(self) -> Any:
        return self._result

    async def execute(self):
        try:
            if inspect.iscoroutinefunction(self._callable_object):
                # Execute coroutine
                print("coroutine function executed")
                async with trio.open_nursery() as nursery:
                    # TODO: need to pass parameters into the coroutine
                    self._result = await self._callable_object()
            else:
                # Execute synchronous function
                print("non-coroutine function executed")
                async with trio.open_nursery() as nursery:
                    # TODO: need to pass parameters into the synchronous function
                    self._result = await trio.to_thread.run_sync(self._callable_object)
        except Exception as e:
            raise e
