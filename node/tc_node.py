from node.base_node import BaseNode
from typing import Callable, Any
from util.async_timing import async_timed
from functools import partial
import logging
import traceback
import inspect
import trio
import sys


class TCNode(BaseNode):
    """
    A wrapper around test cases.
    """

    def __init__(self, callable_object: Callable[..., Any], 
                 name: str,
                 func_parameter_label: str | None=None) -> None:
        super().__init__(name=name,
                         func_parameter_label=func_parameter_label)
        self._callable_object = callable_object
        self.execute = async_timed(self.name)(self.execute)
        self._logger = logging.getLogger("TCNode")
    
    async def execute(self):
        try:
            # TODO: Update unit test to cover signature checking
            func_parameters = {}
            if inspect.signature(self._callable_object).parameters:
                for dependency in self.dependencies:
                    func_parameters[dependency.func_parameter_label] = dependency.result
            if inspect.iscoroutinefunction(self._callable_object):
                # Execute coroutine
                self._logger.info("Executing coroutine")
                async with trio.open_nursery() as nursery: # type: ignore
                    self._result = await self._callable_object(**func_parameters)
            else:
                # Execute synchronous function
                self._logger.info("Executing synchronous function")
                async with trio.open_nursery() as nursery: # type: ignore
                    self._result = await trio.to_thread.run_sync(
                        partial(self._callable_object, **func_parameters)
                        ) # type: ignore
        except Exception as e:
            self.error = e
            _, _, tb = sys.exc_info()
            frames = traceback.extract_tb(tb)
            frame_info = "\n".join(f"Frame {i}:\nFile {frames[i].filename}, "
                                   "line {frames[i].lineno}, "
                                   "in {frames[i].name}\n  {frames[i].line}" \
                                    for i in range(len(frames)))
            self.error_traceback = traceback.format_exc() + "\n" + frame_info
            self._logger.error(f"Error while executing {self.name}: {e}", exc_info=True)

