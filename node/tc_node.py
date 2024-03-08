from node.base_node import BaseNode
from typing import Callable, Any
from util.async_timing import async_timed
from functools import partial
from util.ui_request import UIRequest
import logging
import traceback
import inspect
import trio
import sys


class TCNode(BaseNode):
    """
    A wrapper around test cases.
    """

    def __init__(
        self,
        callable_object: Callable[..., Any],
        name: str,
        func_parameter_label: str | None = None,
    ) -> None:
        super().__init__(name=name, func_parameter_label=func_parameter_label)
        self._callable_object = callable_object
        self.execute = async_timed(self.name)(self.execute)
        self._logger = logging.getLogger("TCNode")

    async def execute(self):
        try:
            # TODO: Update unit test to cover signature checking
            func_parameters = {}
            user_input_required = False
            for _, param in inspect.signature(self._callable_object).parameters.items():
                if param.annotation is UIRequest:
                    user_input_required = True
                    break
        
            if (inspect.signature(self._callable_object).parameters and user_input_required is False) or \
                (len(inspect.signature(self._callable_object).parameters) > 1 and user_input_required is True):
                for dependency in self.dependencies:
                    func_parameters[dependency.func_parameter_label] = dependency.result

            if inspect.iscoroutinefunction(self._callable_object):
                # Execute coroutine
                self._logger.info("Executing coroutine")
                async with trio.open_nursery() as nursery:  # type: ignore
                    if user_input_required:
                        self._result = await self._callable_object(UIRequest(self._ui_request_send_channel), **func_parameters)
                    else:
                        self._result = await self._callable_object(**func_parameters)
            else:
                # Execute synchronous function
                self._logger.info("Executing synchronous function")
                async with trio.open_nursery() as nursery:  # type: ignore
                    if user_input_required:
                        self._result = await trio.to_thread.run_sync(
                            partial(self._callable_object, UIRequest(self._ui_request_send_channel), **func_parameters)
                        )
                    else:
                        self._result = await trio.to_thread.run_sync(
                            partial(self._callable_object,**func_parameters)
                        )  # type: ignore
        except Exception as e:
            self.error = e
            _, _, tb = sys.exc_info()
            frames = traceback.extract_tb(tb)
            frame_info = "\n".join(
                f"Frame {i}:\nFile {frames[i].filename}, "
                "line {frames[i].lineno}, "
                "in {frames[i].name}\n  {frames[i].line}"
                for i in range(len(frames))
            )
            self.error_traceback = traceback.format_exc() + "\n" + frame_info
            self._logger.error(f"Error while executing {self.name}: {e}", exc_info=True)
