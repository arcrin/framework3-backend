# from util.tc_data_broker import TCDataBroker
from util.async_timing import async_timed
from typing import Callable, Any, TYPE_CHECKING
from util.ui_request import UIRequest
from _Node._BaseNode import BaseNode
from functools import partial
import traceback
import logging
import inspect
import trio
import sys

if TYPE_CHECKING:
    from _Application._DomainEntity._TestRun import TestRun


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
        self._execution: int = 0
        # self._data: Dict[Any, Any] = {
        #     "key": str(self.id),
        #     "data": {"name": self.name, "status": True, "progress": 0},
        #     "children": [],
        # }
        self._parent_test_run: "TestRun | None" = None
        self._logger.info(f"TCNode {self.id} created")

    # TODO: TCDataBroker should be replaced by event bus

    @property
    def parent_test_run(self):
        return self._parent_test_run
    
    @parent_test_run.setter
    def parent_test_run(self, value: "TestRun"):
        if not self._parent_test_run:
            self._parent_test_run = value
        else:
            raise Exception("A TCNode can only have one parent TestRun")

    async def execute(self):
        try:
            # TODO: Update unit test to cover function signature check
            func_parameters = {}
            dependency_parameter_labels = [
                d.func_parameter_label
                for d in self.dependencies
                if d.func_parameter_label is not None # type: ignore
            ]  
            for p_name, p_obj in inspect.signature(
                self._callable_object
            ).parameters.items():
                if p_obj.annotation is UIRequest:
                    func_parameters[p_name] = UIRequest(self._ui_request_send_channel)
                else:
                    if p_name in dependency_parameter_labels:
                        for d in self.dependencies:
                            if d.func_parameter_label == p_name:
                                func_parameters[p_name] = d.result

            if inspect.iscoroutinefunction(self._callable_object):
                # Execute coroutine
                self._logger.info("Executing coroutine")
                async with trio.open_nursery() as nursery:  # type: ignore
                    self._result = await self._callable_object(**func_parameters)
            else:
                # Execute synchronous function
                self._logger.info("Executing synchronous function")
                async with trio.open_nursery() as nursery:  # type: ignore
                    self._result = await trio.to_thread.run_sync(
                        partial(self._callable_object, **func_parameters)
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
