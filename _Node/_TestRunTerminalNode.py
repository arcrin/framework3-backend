from _Node._BaseNode import BaseNode
from _Application._SystemEvent import TestRunTerminationEvent
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from _Application._DomainEntity._TestRun import TestRun
    from _Node._BaseNode import NodeState


class TestRunTerminalNode(BaseNode):
    def __init__(self, test_run: "TestRun"):
        super().__init__("TestRunTerminalNode")
        self._test_run = test_run
        self._logger = logging.getLogger("TestRunTerminalNode")

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value: "NodeState"):
        self._state = value

    async def execute(self):
        self._logger.info(f"Executing TestRunTerminalNode {self.id}")
        test_run_termination_event = TestRunTerminationEvent(
            {"tr_id": self._test_run.id}
        )  # type: ignore
        assert (
            self._test_run.parent_panel is not None
        ), "TestRunTerminalNode must be associated with a panel"
        self._test_run.parent_panel.remove_test_run()
        await self._event_bus.publish(test_run_termination_event)
