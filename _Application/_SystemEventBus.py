from _Application._SystemEvent import BaseEvent
from typing import Callable, List, Coroutine, Any


class SystemEventBus:
    def __init__(self):
        self._listeners: List[Callable[[BaseEvent], Coroutine[Any, Any, None]]] = []

    def subscribe(
        self, listener: Callable[[BaseEvent], Coroutine[Any, Any, None]]
    ):
        self._listeners.append(listener)
        

    async def publish(self, event: BaseEvent):
        for listener in self._listeners:
            await listener(event)
