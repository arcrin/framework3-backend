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
        
"""
This implementation is a classic example of an event bus designed for  asynchronous event-driven systems.

Strengths of the Current Implementation
1. Singleton Design:
    - Ensures there is only one SystemEventBus instance, centralizing event management.

2. Dynamic Subscription Model:
    - Supports runtime subscription of handlers to specific event types.
    - Flexible enough to accommodate new event types and handlers without requiring modifications to the core logic. 
    
3. Asynchronous Event Publishing:
    - publish leverages asynchronous handlers, making it suitable for concurrent and non-blocking operations.

4. Event-Type Specific Handling:
    - Each event type can have its own set of handlers, allowing precise control over event processing.

5. Minimal Overhead:
    - The implementation is lightweight, avoiding unnecessary complexity.

    
Potential Improvements:
1. Add Unsubscribe Functionality
    - Currently, there's no way to remove a handler for a specific event type, which can lead to memory leaks or stale subscriptions.

    Solution:
        @classmethod
        def unsubscribe_from_event(cls, event_type: Type[BaseEvent], event_handler: Callable[[BaseEvent], Any]):
            if event_type in cls._listeners:
                cls._listeners[event_type].remove(event_handler)
                if not cls._listeners[event_type]:
                    del cls._listeners[event_type]

2. Handle Handler Failures Gracefully
    - If a handler raises an exception, it could disrupt the event publishing loop.

    Solution:
        - use try-except around each handler invocation to isolate failures:

        @classmethod
        async def publish(cls, event: BaseEvent):
            for handler in cls._listener.get(type(event), []):
                try:
                    await handler(event)
                except Exception as e:
                    # Log the failure without distrupting other handlers
                    print(f"Handler {handler} failed for event {event}: {e})
                    
3. Allow Wildcard Subscriptions:
    - Currently, you can only subscribe to specific event types. Adding support for "catch-all" subscriptions can be helpful for logging, 
    debugging, or analytics.
    
    Solution:
            - Introduce a BaseEvent wildcard subscription:
                
                @classmethod
                def subscribe_to_all_events(cls, event_handler: Callable[[BaseEvent], Any]):
                    cls.subscribe_to_event(BaseEvent, event_handler)
                    

    4. Support Prioritized Event Handling:
        - Handlers are invoked in the order they were added. Adding support for priorities allows more critical handlers to execute first.

        Solution:
        - Use a PriorityQueue or maintain a sorted list of handlers:

            import heapq

            _listeners: Dict[Type[BaseEvent], List[Tuple[int, Callable[[BaseEvent], Any]]]] = {}
            
            @classmethod
            def subscribe_to_event(cls, event_type: Type[BaseEvent], event_handler: Callable[[BaseEvent], Any], priority: int=0):
                if event_type not in cls._listeners:
                    cls._listeners[event_type] = []
                heapq.heappush(cls._listeners[event_type], (priority, event_handler))

            @classmethod
            async def publish(cls, event: BaseEvent):
            if type(event) in cls._listeners:
                for _, handler in sorted(cls._listeners[type(event)]):  # Sort by priority
                    try:
                        await handler(event)
                    except: Exception as e:
                        print(f"Handler {handler} failed for event {event}: {e}")


5. Add Delivery Guarantees (Optional)
    - If handlers fail or events are dropped, consider adding delivery confirmation or retry logic.
    
    Solution:
        - Track the delivery status of each handler and retry failed ones (requires state management).

            @classmethod
            async def publish(cls, event: BaseEvent):
                for handler in cls._listeners.get(type(event), []):
                    success = False
                    for _ in range(3):
                        try:
                           await handler(event)
                           success = True
                           break
                        except Exception as e:
                            print(f"Retrying handler {handler} for event {event}: {e}")
                    if not success:
                        print(f"Handler {handler} failed for event {event}")


6. Improve Debugging and Logging
    - Add logging for when events are published, subscriptions occur, or errors happen.

    Solution:
    - Use Python's logging module to centralize debug information:
        
        import logging 

        logger = logging.getLogger("SystemEventBus")

        @classmethod
        async def publish(cls, event: BaseEvent):
            logger.info(f"Publishing event: {event}")
            for handler in cls._listeners.get(type(event), []):
                try:
                    await handler(event)
                    logger.info(f"Handler {handler} successfully processed {event}")
                except Exception as e:
                    logger.error(f"Handler {handler} failed for event {event}: {e}")


Final Refined Implementation

    from typing import Callable, List, Any, TypeVar, Dict, Tuple
    import logging
    import heapq

    E = TypeVar("E", bound="BaseEvent")


    class BaseEvent:
        def __init__(self, payload: Any):
            self.payload = payload


    class SystemEventBus:
        _instance = None
        _listeners: Dict[Type[BaseEvent], List[Tuple[int, Callable[[BaseEvent], Any]]]] = {}
        _logger = logging.getLogger("SystemEventBus")

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super(SystemEventBus, cls).__new__(cls)
            return cls._instance
  
        @classmethod
        async def publish(cls, event: BaseEvent):
            cls._logger.info(f"Publishing event: {type(event).__name__}")
            for _, handler in sorted(cls._listeners.get(type(event), [])):
                try:
                    await handler(event)
                    cls._logger.info(f"Handler {handler} successfully processed {event}")
                except Exception as e:
                    cls._logger.error(f"Handler {handler} failed for event {event}: {e}")

        @classmethod
        def subscribe_to_event(cls, event_type: Type[BaseEvent], event_handler: Callable[[BaseEvent], Any], priority: int = 0):
            if event_type not in cls._listeners:
                cls._listeners[event_type] = []
            heapq.heappush(cls._listeners[event_type], (priority, event_handler))
            cls._logger.info(f"Subscribed {event_handler} to event {event_type.__name__}")

        @classmethod
        def unsubscribe_from_event(cls, event_type: Type[BaseEvent], event_handler: Callable[[BaseEvent], Any]):
            if event_type in cls._listeners:
                cls._listeners[event_type] = [
                    item for item in cls._listeners[event_type] if item[1] != event_handler
                ]
                if not cls._listeners[event_type]:
                    del cls._listeners[event_type]
                cls._logger.info(f"Unsubscribed {event_handler} from event {event_type.__name__}")
"""