from _Node._TestRunTerminalNode import TestRunTerminalNode
from _Application._SystemEvent import NewTestCaseEvent
from typing import List, TYPE_CHECKING, Dict, cast
from uuid import uuid4
import logging

if TYPE_CHECKING:
    from _Application._DomainEntity._Panel import Panel
    from _Application._SystemEventBus import SystemEventBus
    from _Node._TCNode import TCNode
    from _Node._BaseNode import BaseNode
    from trio import MemorySendChannel


class TestRun:
    def __init__(
        self,
        node_executor_send_channel: "MemorySendChannel[BaseNode]",
        ui_request_send_channel: "MemorySendChannel[str]",
        event_bus: "SystemEventBus",
        test_profile,  # type: ignore
    ):
        self._id: str = uuid4().hex
        self._tc_nodes: List["TCNode"] = []
        self._failed_tasks: Dict[str, "TCNode"] = {}
        self._node_executor_send_channel = node_executor_send_channel
        self._ui_request_send_channel = ui_request_send_channel
        self._event_bus = event_bus
        self._parent_panel: "Panel" = cast("Panel", None)
        # TODO: profile is downloaded once and stored somewhere, either Panel or Session
        self._test_profile = test_profile  # type: ignore
        self._logger = logging.getLogger("TestRun")
        self._test_run_terminal_node = TestRunTerminalNode(self)
        self._test_run_terminal_node.event_bus = self._event_bus
        self._test_run_terminal_node.set_scheduling_callback(
            self._node_scheduling_callback
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def parent_panel_id(self) -> int:
        return self._parent_panel.id

    @property
    def parent_control_session_id(self) -> str:
        return self._parent_panel.parent_control_session.id

    @property
    def parent_panel(self) -> "Panel":
        return self._parent_panel

    @parent_panel.setter
    def parent_panel(self, value: "Panel"):
        if not self._parent_panel:
            self._parent_panel = value
        else:
            raise Exception("A test run can only have one parent panel")

    def add_to_failed_test_cases(self, tc_node: "TCNode"):
        self._failed_tasks[tc_node.id] = tc_node
        self._tc_nodes.remove(tc_node)

    async def retest_failed_test_cases(self, tc_id: str):
        tc_node = self._failed_tasks[tc_id]
        await self.add_tc_node(tc_node)
        self._failed_tasks.pop(tc_id)

    async def add_tc_node(self, tc_node: "TCNode"):  # TODO: add test case event
        self._test_run_terminal_node.add_dependency(tc_node)
        self._tc_nodes.append(tc_node)
        tc_node.set_scheduling_callback(self._node_scheduling_callback)
        tc_node.data_model.parent_test_run = self
        tc_node.ui_request_send_channel = self._ui_request_send_channel
        tc_node.event_bus = self._event_bus
        assert tc_node.event_bus is not None, "TCNode must have event bus"
        await tc_node.check_dependency_and_schedule_self()
        new_test_case_event = NewTestCaseEvent(tc_node)
        await self._event_bus.publish(new_test_case_event)

    async def load_test_case(self):
        profile = self._test_profile()  # type: ignore
        for tc_node in profile.test_case_list:  # type: ignore
            await self.add_tc_node(tc_node)  # type: ignore

    async def _node_scheduling_callback(self, node: "BaseNode"):
        await self._node_executor_send_channel.send(node)
