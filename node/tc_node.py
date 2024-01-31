from node.base_node import BaseNode
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor

# from functools import partial
import asyncio


class TCNode(BaseNode):
    """
    A wrapper around test cases.
    """

    def __init__(self, callable_object: Callable[..., Any]) -> None:
        super().__init__(callable_object.__name__)
        self._callable_object = callable_object
        self._result: Any = None

    @property
    def result(self) -> Any:
        return self._result

    async def execute(self):
        try:
            if asyncio.iscoroutinefunction(self._callable_object):
                self._result = await self._callable_object()
            else:
                with ThreadPoolExecutor() as pool:
                    self._result = await asyncio.get_running_loop().run_in_executor(
                        pool, self._callable_object
                    )
        except Exception as e:
            raise e
