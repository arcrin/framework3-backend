from _Application._SystemEvent import BaseEvent
from typing import Callable, List, Any, TypeVar, Type, Dict

E = TypeVar("E", bound=BaseEvent)
F = TypeVar('F', bound=Callable[..., Any])

class SystemEventBus:
    _instance = None
    _listeners: Dict[Type[BaseEvent], List[Callable[[BaseEvent], Any]]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemEventBus, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    async def publish(cls, event: BaseEvent):
        # TODO: delivery check?
        for handler in cls._listeners.get(type(event), []):
            await handler(event)

    @classmethod
    def subscribe_to_event(cls, event_type: Type[BaseEvent], event_handler: Callable[[BaseEvent], Any]):  
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        cls._listeners[event_type].append(event_handler)