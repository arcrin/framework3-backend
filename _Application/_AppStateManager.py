from _Application._SystemEvent import NewTestCaseEvent
from _Application._SystemEventBus import SystemEventBus
from _Application._SystemEvent import BaseEvent
from typing import TYPE_CHECKING, Dict, Any
import trio
import logging

if TYPE_CHECKING:
    from trio import MemorySendChannel


class ApplicationStateManager:
    def __init__(self, event_bus: SystemEventBus,
                 tc_data_send_channel: "MemorySendChannel[Dict[Any, Any]]",):
        self._app_state = {}
        self._control_context = {}
        self._app_data = {}
        self._event_bus = event_bus
        self._tc_data_send_channel = tc_data_send_channel
        self._event_bus.subscribe(self.event_handler)
        self._logger = logging.getLogger("ApplicationStateManager")
        

    async def event_handler(self, event: BaseEvent):
        if isinstance(event, NewTestCaseEvent):
            self._logger.info(f"New test case added to test run {event.payload["test_name"]}")
            async with trio.open_nursery() as nursery:
                nursery.start_soon(self._tc_data_send_channel.send, {"type": "tcData", "message": event.payload})
            