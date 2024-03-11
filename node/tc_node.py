from node.base_node import BaseNode
from typing import Callable, Any, Dict
from util.async_timing import async_timed
from functools import partial
from util.ui_request import UIRequest
from util.tc_data_broker import TCDataBroker
import traceback
import logging
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
        self._tc_data_broker: TCDataBroker | None = None
        self._execution: int = 0
        self._data: Dict[Any, Any] = {
            "key": str(self.id),
            "data": {"name": self.name, "status": True, "progress": 0},
            "children": [],
        }

    @property
    def tc_data_broker(self) -> TCDataBroker | None:
        return self._tc_data_broker

    @tc_data_broker.setter
    def tc_data_broker(self, value: TCDataBroker):
        self._tc_data_broker = value
        self._tc_data_broker.tc_data = self._data

    async def execute(self):
        try:
            # TODO: Update unit test to cover signature checking
            if self._tc_data_broker is not None:
                self._execution += 1
                execution_data = {  # type: ignore
                    "key": self._execution,
                    "data": {
                        "name": f"execution {self._execution}",
                    },
                    "children": [],
                }
                await self._tc_data_broker.update_test_case()
                await self._tc_data_broker.update_execution(execution_data)  # type: ignore
            else:
                raise Exception(
                    f"A data model needs to be assigned to test node{self.name}"
                )

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
                elif p_obj.annotation is TCDataBroker:
                    func_parameters[p_name] = self._tc_data_broker
                else:
                    if p_name in dependency_parameter_labels:
                        for d in self.dependencies:
                            if d.func_parameter_label == p_name:
                                func_parameters[p_name] = d.result

            # user_input_required = False
            # for _, param in inspect.signature(self._callable_object).parameters.items():
            #     if param.annotation is UIRequest:
            #         user_input_required = True
            #         break

            # if (
            #     inspect.signature(self._callable_object).parameters
            #     and user_input_required is False
            # ) or (
            #     len(inspect.signature(self._callable_object).parameters) > 1
            #     and user_input_required is True
            # ):
            #     for dependency in self.dependencies:
            #         func_parameters[dependency.func_parameter_label] = dependency.result

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
