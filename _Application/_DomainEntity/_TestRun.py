from _Node._TerminalNode import TerminalNode
from _Application._SystemEvent import NewTestCaseEvent
from typing import List, TYPE_CHECKING
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
        test_profile,
    ):  # type: ignore
        self._id: str = uuid4().hex
        self._tc_nodes: List["TCNode"] = []
        self._terminal_node = TerminalNode()
        self._node_executor_send_channel = node_executor_send_channel
        self._ui_request_send_channel = ui_request_send_channel
        self._event_bus = event_bus
        self._parent_panel: Panel | None = None
        # TODO: profile is downloaded once and stored somewhere, either Panel or Session
        self._test_profile = test_profile  # type: ignore
        self._logger = logging.getLogger("TestRun")

    @property
    def id(self) -> str:
        return self._id

    @property
    def parent_panel(self) -> "Panel | None":
        return self._parent_panel

    @parent_panel.setter
    def parent_panel(self, value: "Panel"):
        if not self._parent_panel:
            self._parent_panel = value
        else:
            raise Exception("A test run can only have one parent panel")

    async def add_tc_node(self, tc_node: "TCNode"):  # TODO: add test case event
        self._terminal_node.add_dependency(tc_node)
        self._tc_nodes.append(tc_node)
        tc_node.set_scheduling_callback(self._node_scheduling_callback)
        tc_node.data_model.parent_test_run = self
        tc_node.ui_request_send_channel = self._ui_request_send_channel
        tc_node.event_bus = self._event_bus
        assert tc_node.event_bus is not None, "TCNode must have event bus"
        new_test_case_event = NewTestCaseEvent(
            {
                "id": tc_node.id,  # type: ignore
                "name": tc_node.name,  # type: ignore
                "tr_id": tc_node.data_model.parent_test_run.id, # type: ignore
                "panel_id": tc_node.data_model.parent_test_run.parent_panel.id, # type: ignore
                "session_id": tc_node.data_model.parent_test_run.parent_panel.parent_control_session.id # type: ignore
            }
        )
        await self._event_bus.publish(new_test_case_event)
        await tc_node.check_dependency_and_schedule_self()

    async def load_test_case(self):
        profile = self._test_profile()  # type: ignore
        for tc_node in profile.test_case_list:  # type: ignore
            await self.add_tc_node(tc_node)  # type: ignore

    async def _node_scheduling_callback(self, node: "BaseNode"):
        await self._node_executor_send_channel.send(node)
