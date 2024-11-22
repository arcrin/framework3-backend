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


"""
The Session, ControlSession, and ViewSession classes are well-structured and capture the roles of different session types effectively.

Key Elements in Each Class
1. Session Base Class:
    - The Session class defines a unique ID (uuid4().hex) and a WebSocket connection, which currently serves as the primary communication method.
    - This base class establishes the foundation for different session types, enabling clear distinctions between control and view sessions.

2. ControlSession:
    - Extends Session to introduce control-specific attributes, such as _panels (list of Panel objects), _panel_limit (the maximum number of panels),
    and _test_profile.
    - The add_panel method manages panel creation within the session. It ensures the number of panels doesn't exceed _panel_limit, raises an error if 
    the limit is exceeded, and lo9gs each addition.
    - Panel Labeling: There's a TODO regarding how panels are labeled. Depending on how you want to identify panels, you may choose to generate 
    unique IDs based on panel positions or test jig mappings.

3. ViewSession:
    - A lightweight session that extends Session without any additional functionality beyond logging.
    - It provides flexibility for UI connections that don't need control access but still benefit from a dedicated session structure.
    
Suggestions for Improvements
1. Support for Additional Communication Types:
    - In Session, you noted a TODO regarding support for other communication tpes beyond WebSocket. To add flexibility, consider using a communication 
    interface instead of directly passing WebSocketConnection. This interface could define a common send or receive method, which different communication
    protocols implement.

        class CommunicationInterface(ABC):
            @abstractmethod
            async def send(self, message: str) -> None:
                pass
                
            @abstractmethod
            async def receive(self) -> str:
                pass
                
    Then, different connection types could implement CommunicationInterface, allowing Session to interact with any communication type transparently.
    
2. Session and Panel Lifecycle Management:
    - Consider adding explicit start and end methods to manage session lifecycle events, including resource cleanup and logging. For ControlSession, 
    this could involve stopping all associated panels or resetting configurations.
    - Example for session cleanup:

        async def end(self):
            # Close connections or perform any necessary cleanup
            self._logger.info(f"Ending session {self._id}")

3. Error Handling in add_panel:
    - If panel addition fails due to an exception (like the panel limit being reached), consider logging a more descriptive error message  to provide
    context in the logs.          

4. Panel ID and Labeling Strategy:
    - To resolve the TODO on panel labeling, you might want to standardize panel IDs based on their positions in the test jig or a defined order.
    For example, panels could be labeled based on their physical placement on the jig or assigned sequential IDs that persist across sessions.
    
5. Session-Specific Settings:
    - If different sessions have specific configuration needs (e.g., timeout values or test settings for a ControlSession), consider defining a 
    session configuration object that holds these parameters. This object could make it easier to manage per-session settings as the system grows.

6. ViewSession Monitoring:
    - In ViewSession, you could add optional attributes for monitoring purposes, like connection timestamps or activeity logs, if there's a need 
    to keep track of view-only sessions for UI analytics.

Example Adjusted ControlSession with Communication Interface and Lifecycle Management

    class ControlSession(Session):
        def __init__(
            self,
            communication_interface: CommunicationInterface,
            test_profile,
            panel_limit: init = 1,
        ):
            super().__init__(communication_interface)
            self._panels: List[Panel] = []
            self._panel_limit = panel_limit
            self._test_profile = test_profile
            self._logger = logging.getLogger("ControlSession")
            for i in range(panel_limit):
                self._add_panel()
        
        async def start(self):
            self._logger.info(f"Starting ControlSession {self.id}")
            # Any additional startup logic

        async def end(self):
            self._logger.info(f"Ending ControlSession {self.id}")
            for panel in self._panels:
                await panel.cleanup()   # Hypothetical cleanup method in Panel

        def add_panel(self):
            if len(self._panels) >= self._panel_limit:
                error_message = f"Test jig only supports {self._panel_limit} panel{'s' if self._panel_limit > 1 else ''}"
                self._logger.error(error_message)
                raise Exception(error_message)
            panel_id = len(self._panels) + 1
            new_panel = Panel(panel_id, self._test_profile)
            self._panels.append(new_panel)
            self._logger.info(f"Panel {new_panel.id} added)
            new_panel.parent_control_session = self

        
"""