from _Application._SystemEventBus import SystemEventBus
from typing import TYPE_CHECKING, cast, List
from _Application._DomainEntity._TestRun import TestRun
import logging

if TYPE_CHECKING:
    from _Application._DomainEntity._Session import ControlSession
    from _Application._DomainEntity._TestRun import TestRun
    from _Node._TCNode import TCNode


class Panel:
    def __init__(
        self,
        panel_id: int,
        test_profile,  # type: ignore
    ):
        self._id = panel_id
        self._test_run: "TestRun | None" = None
        self._parent_control_session: "ControlSession" = cast("ControlSession", None)
        self._event_bus = SystemEventBus()
        self._test_profile = test_profile  # type: ignore
        self._logger = logging.getLogger("Panel")
        # TODO: test jig hard ware related code should be in this class

    @property
    def id(self):
        return self._id

    @property
    def parent_control_session_id(self):
        return self._parent_control_session.id

    @property
    def parent_control_session(self):
        return self._parent_control_session

    @property
    def test_run(self):
        return self._test_run
    
    @property
    def tc_nodes(self) -> List["TCNode"]:
        if self._test_run:
            return self._test_run.tc_nodes
        else:
            raise ValueError(f"Not test run associated with panel {self.id}")

    @parent_control_session.setter
    def parent_control_session(self, value: "ControlSession"):
        self._parent_control_session = value

    async def add_test_run(self):
        if not self._test_run:
            self._test_run = TestRun(
                self._test_profile,  # type: ignore
            )
            self._logger.info(f"TestRun {self._test_run.id} added")
            self._test_run.parent_panel = self
        else:
            raise Exception("A panel can only have one test run")

    def remove_test_run(self):
        self._test_run = None
        self._logger.info("TestRun removed")
