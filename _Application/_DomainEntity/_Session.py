from _Application._SystemEventBus import SystemEventBus
from _Application._DomainEntity._Panel import Panel
from typing import List, TYPE_CHECKING
from uuid import uuid4
import logging

if TYPE_CHECKING:
    from _Application._DomainEntity._Panel import Panel
    from trio_websocket import WebSocketConnection  # type: ignore


class Session:
    def __init__(
        self, ws_connection: "WebSocketConnection"
    ):  # TODO: need to include more communication types
        self._id = uuid4().hex
        self._logger = logging.getLogger("Session")
        self._connection = ws_connection

    @property
    def id(self):
        return self._id

    @property
    def connection(self):
        return self._connection


class ControlSession(Session):
    def __init__(
        self,
        ws_connection: "WebSocketConnection",
        test_profile,  # type: ignore
        panel_limit: int = 1,
    ):
        super().__init__(ws_connection)
        self._panels: List[Panel] = []
        self._logger = logging.getLogger("ControlSession")
        self._panel_limit = panel_limit
        self._event_bus = SystemEventBus()
        self._test_profile = test_profile  # type: ignore
        for i in range(panel_limit):
            self._logger.info(f"Adding panel {i + 1}")
            self.add_panel()

    @property
    def panels(self):
        return self._panels

    # Creating new panel in a control session
    def add_panel(self):
        if len(self._panels) >= self._panel_limit:
            error_message = f"Test jig only support {self._panel_limit} panel{'' if self._panel_limit == 1 else 's'}"
            self._logger.error(error_message)
            raise Exception(error_message)
        else:
            panel_id = self._panel_limit - len(
                self._panels
            )  # TODO: depends on how we label the panels on the test jig
            new_panel = Panel(
                panel_id,
                self._test_profile,  # type: ignore
            )
            self._panels.append(new_panel)
            self._logger.info(f"Panel {new_panel.id} added")
            new_panel.parent_control_session = self


class ViewSession(Session):
    def __init__(self, ws_connection: "WebSocketConnection"):
        super().__init__(ws_connection)
        self._logger = logging.getLogger("ViewSession")
