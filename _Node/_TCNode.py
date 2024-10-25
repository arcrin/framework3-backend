from _Application._DomainEntity._TestCaseDataModel import TestCaseDataModel
from typing import Callable, Any
from _Application._SystemEvent import TestCaseFailEvent
from _Application._SystemEventBus import SystemEventBus
from util.async_timing import async_timed
from _Node._BaseNode import BaseNode, NodeState
from functools import partial
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
        description: str = "",
    ) -> None:
        super().__init__(name=name, func_parameter_label=func_parameter_label)
        self._data_model = TestCaseDataModel(self._id, self._name, description)
        self._callable_object = callable_object
        self.execute = async_timed(self.name)(self.execute)
        self._logger = logging.getLogger("TCNode")
        self._logger.info(f"TCNode {self.id} created")
        self._auto_retry_count: int = 1
        self._data_model.state = NodeState.NOT_PROCESSED


    @property
    def state(self) -> NodeState:
        return self._data_model.state
    
    @state.setter
    def state(self, value: NodeState) -> None:
        self._data_model.state = value

    @property
    def auto_retry_count(self) -> int:
        return self._auto_retry_count

    @property
    def data_model(self) -> TestCaseDataModel:
        return self._data_model
    
    async def quarantine(self) -> None:
        assert self._data_model.parent_test_run is not None, "TCNode must be associated with a test run"
        self._data_model.parent_test_run.add_to_failed_test_cases(self)
        self.mark_as_failed()
        test_case_failed_event = TestCaseFailEvent({"tc_id": self.id})
        await SystemEventBus.publish(test_case_failed_event)

    async def execute(self):
        self.mark_as_processing()
        await self.data_model.add_execution()
        self._auto_retry_count -= self.data_model.current_execution.execution_id
        assert (
            self.data_model.parent_test_run is not None
        ), "TCNode must be associated with a test run"

        try:
            # TODO: Update unit test to cover function signature check
            func_parameters = {}
            dependency_parameter_labels = [
                d.func_parameter_label
                for d in self.dependencies
                if d.func_parameter_label is not None  # type: ignore
            ]
            for p_name, p_obj in inspect.signature(
                self._callable_object
            ).parameters.items():
                if p_obj.annotation is TestCaseDataModel:
                    func_parameters[p_name] = self.data_model
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
