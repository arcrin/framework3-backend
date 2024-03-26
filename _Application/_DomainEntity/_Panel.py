from typing import TYPE_CHECKING
from _Application._DomainEntity._TestRun import TestRun
import logging

if TYPE_CHECKING:
    from _Application._DomainEntity._Session import ControlSession
    from _Application._DomainEntity._TestRun import TestRun
    from _Application._SystemEventBus import SystemEventBus
    from trio import MemorySendChannel
    from _Node._BaseNode import BaseNode


class Panel:
    def __init__(
        self,
        panel_id: int,
        node_executor_send_channel: "MemorySendChannel[BaseNode]",
        ui_request_send_channel: "MemorySendChannel[str]",
        event_bus: "SystemEventBus",
        test_profile, # type: ignore
    ):  
        self._id = panel_id
        self._test_run: "TestRun | None " = (
            None  # COMMENT: each panel can only have one TestRun
        )
        self._parent_control_session: "ControlSession | None" = None
        self._node_executor_send_channel = node_executor_send_channel
        self._ui_request_send_channel = ui_request_send_channel
        self._event_bus = event_bus
        self._test_profile = test_profile  # type: ignore
        self._logger = logging.getLogger("Panel")
        # TODO: test jig hard ware related code should be in this class

    @property
    def id(self):
        return self._id

    @property
    def parent_control_session(self):
        return self._parent_control_session

    @property
    def test_run(self):
        return self._test_run

    @parent_control_session.setter
    def parent_control_session(self, value: "ControlSession"):
        self._parent_control_session = value

    async def add_test_run(self):
        if not self._test_run:
            self._test_run = TestRun(
                self._node_executor_send_channel,
                self._ui_request_send_channel,
                self._event_bus,
                self._test_profile, # type: ignore
            )  
            self._logger.info(f"TestRun {self._test_run.id} added")
            self._test_run.parent_panel = self
        else:
            raise Exception("A panel can only have one test run")

    def remove_test_run(self):
        self._test_run = None
        self._logger.info("TestRun removed")
