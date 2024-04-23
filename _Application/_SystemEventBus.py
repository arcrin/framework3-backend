from _Application._SystemEvent import BaseEvent
from typing import Callable, List, Coroutine, Any


class SystemEventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemEventBus, cls).__new__(cls)
            cls._instance.init()
        return cls._instance
    
    def init(self):
        self._listeners: List[Callable[[BaseEvent], Coroutine[Any, Any, None]]] = []

    def subscribe(
        self, listener: Callable[[BaseEvent], Coroutine[Any, Any, None]]
    ):
        self._listeners.append(listener)
        

    async def publish(self, event: BaseEvent):
        # TODO: delivery check?
        for listener in self._listeners:
            await listener(event)
