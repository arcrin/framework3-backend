from abc import ABC
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from _Node._BaseNode import BaseNode
    from _Node._TCNode import TCNode
    from _Application._DomainEntity._TestCaseDataModel import TestCaseDataModel
    from util._InteractionContext import InteractionContext
    from _Application._DomainEntity._Session import ViewSession


class BaseEvent(ABC):
    def __init__(self, payload):  # type: ignore
        self._payload = payload

    @property
    def payload(self):
        return self._payload


class NewTestCaseEvent(BaseEvent):
    def __init__(self, payload: "TCNode"):  
        super().__init__(payload)

class NodeReadyEvent(BaseEvent):
    def __init__(self, payload: "BaseNode"):
        super().__init__(payload)


class NewTestExecutionEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)

class ParameterUpdateEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)


class ProgressUpdateEvent(BaseEvent):
    def __init__(self, payload: "TestCaseDataModel"):
        super().__init__(payload)

class TestCaseFailEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)   


class TestRunTerminationEvent(BaseEvent):
    def __init__(self, payload):  # type: ignore
        super().__init__(payload)

class UserInteractionEvent(BaseEvent):
    def __init__(self, payload: "InteractionContext"): 
        super().__init__(payload)

class UserResponseEvent(BaseEvent):
    def __init__(self, payload: Dict[str, str]):  # type: ignore
        super().__init__(payload)

class NewViewSessionEvent(BaseEvent):
    def __init__(self, payload: "ViewSession"): 
        super().__init__(payload)
        
        
"""
Strength of the Current Implementation
1. Consistent Base Class (Base Event):
    - All events inherit from BaseEvent, ensuring consistency 
    - This provides a unified interface for events and simplifies processing by the SystemEventBus

2. Typed Events:
    - Specific event classes like NewTestCaseEvent, ProgressUpdateEvent, and TestRunTerminationEvent are well-named and descriptive, making
    the purpose of each event clear.

3. Alignment with Domain and Workflow:
    - Events map directly to significant actions or states in your system (e.g., NodeReadyEvent for workflow readiness, UserInteractionEvent 
    for UI requests).
    
4. Extendability:
    - Adding new events is straightforward due to the common BaseEvent structure.

5. Payload Flexibility:
    - The design allows diverse payloads, from TestCaseDataModel to dictionaries and specific domain entities like InteractionContext.

Potential Areas for Improvement
1. Event-Specific Attributes
    - Currently, all events use a generic payload property. WHile flexible, this design doesn't enforce specific payload types or structures
    for each event.
    - For example, ProgressUpdateEvent could expose a progress attribute derived from its payload (TestCaseDataModel).

    Solution:
    - Add event-specific properties or methods for easier and more explicit access to payload data.
    - Example:
        class ProgressUpdateEvent(BaseEvent):
            def __init__(self, payload: "TestCaseDataModel"):
                super().__init__(payload)

            @property
            def progress(self):
                return self.payload.progress

2. Standardizing Event Initialization:
    - The constructors of the event classes are repetitive, especially when the base class already handles the payload.
    - Consider defining event classes with just their specific types and reusing the BaseEvent constructor.

    Solution:
        class NodeReadyEvent(BaseEvent):
            pass

3. Event Categorization:
    - Events are diverse, ranging from workflow-specific (NodeReadyEvent) to UI-related (UserInteractionEvent).
    - Categorizing events (e.g., Workflow, UI, System) can help organize the codebase and make subscription easier to manage.
    
    Solution:
    - Use namespaces, folders, or naming conventions to separate event types.
    - Example:
        - WorkflowEvents.NodeReadyEvent
        - UIEvents.UserInteractionEvent

4. Stronger Type Enforcement:
    - The current implementation uses inline type: ignore for some payloads, which can lead to loose typing and potential runtime errors.
    - Use proper type annotations and enforce stricter type checks to improve maintainability.

5. Add Event Metadata (Optional)
    - Include optional metadata like a timestamp or source in the BaseEvent class for better debugging or audit trails.
    Solution:
        form datetime import datetime

        class __init__(ABC):
            def __init__(self, payload):
                self._payload = payload
                self._timestamp = datetime.now()

            @property
            def payload(self):
                return self._payload

            @property
            def timestamp(self):
                return self._timestamp

Refined Example

form abc import ABC
form typing import TYPE_CHECKING, Any
from datetime import datetime

if TYPE_CHECKING:
    form _Node._BaseNode import BaseNode
    from _Application._DomainEntity._TestCaseDataModel import TestCaseDataModel
    from util._InteractionContext import InteractionContext


class BaseEvent(ABC):
    def __init__(self, payload: Any):
        self._payload = payload
        self._timestamp = datetime.now()

    @property
    def payload(self) -> Any:
        return self._payload

    @property
    def timestamp(self) -> datetime:
        return self._timestamp
        

# Workflow Events
class NodeReadyEvent(BaseEvent):
    def __init__(self, payload: "BaseNode"):
        super().__init__(payload)

    @property
    def node(self) -> "BaseNode":
        return self.payload

        
class NewTestCaseEvent(BaseEvent):
    def __init__(self, payload: "TestCaseDataModel"):
        super().__init__(payload)

    @property
    def test_case(self) -> "TestCaseDataModel":
        return self.payload


# UI Events
class UserInteractionEvent(BaseEvent):
    def __init__(self, payload: "InteractionContext")
        super().__init__(payload)

    @property
    def context(self) -> "InteractionContext":
        return self.payload


class UserResponseEvent(BaseEvent):
    def __init__(self, payload: dict):
        super().__init__(payload)

    @property
    def response(self) -> dict:
        return self.payload


        
Benefits of the Refinements
1. Explicit Payload Properties:
    - Each event exposes domain-specific properties, reducing te need for consumers to unpack generic payloads.

2. Improved Organization:
    - Workflow and UI events are separated for clarity.

3. Enhanced Debugging:
    - The timestamp property provides valuable metadata for event tracking.

4. Reduced Redundancy:
    - By relying on the BaseEvent constructor, event-specific logic is minimized.
    

Why Categorization is Important
1. Improved Discoverability:
    - Helps developers quickly locate relevant events, especially in larger systems.

2. Easier Subscription Management:
    - Grouping events by category (e.g., Workflow, UI) makes it easier to subscribe to the relevant events.

3. Scalability:
    - As your system grows, event categorization prevents a monolithic structure.

Options for Categorization
1. Python Modules (Preferred for Scalability)
    - What: Organize events into separate files (modules) based on their category, e.g., workflow_events.py, ui_events.py.
    - How: User Python packages to group related files together. For example:
    Folder Structure:
        events/
            __init__.py
            workflow.py
            ui.py
            system.py

    Example Code:
        - workflow.py
        
        from .base import BaseEvent
        form typing import TYPE_CHECKING

        if TYPE_CHECKING:
            from _Node._BaseNode import BaseNode
        
        
        class NodeReadyEvent(BaseEvent): 
            def __init__(self, payload: "BaseNode")
                super().__init__(payload)


        - ui.py

        form .base import BaseEvent
        from typing import TYPE_CHECKING

        if TYPE_CHECKING:
            from util._InteractionContext import InteractionContext         
            
        
        class UserInteractionEvent(BaseEvent):
            def __init__(self, payload: "InteractionContext"):
                super().__init__(payload)

Usage:
    from events.workflow import NodeReadyEvent
    from events.ui import UserInteractionEvent

    - Pros:
        - Keeps each event type logically separate.
        - Easier to manage in large systems with many events.

    - Cons:
        - Slightly more boilerplate (e.g., importing base classes into each module).


2. Classes as Namespaces
    - What: Use classes purely for grouping events by category, with each event as a nested class.
    - How:
        class WorkflowEvents:
            class NodeReadyEvent(BaseEvent):
                def __init__(self, payload: "BaseNode"):
                    super().__init__(payload)

        
        class UIEvents:
            class UserInteractionEvent(BaseEvent):
                def __init__(self, payload: "InteractionContext"):
                    super().__init__(payload)

Usage:

        from events import WorkflowEvents, UIEvents

        event = WorkflowEvents.NodeReadyEvent(payload)

    - Pros:
        - Keeps related events visually grouped in the same file.
        - Easier for small-to-medium systems where splitting into modules feels excessinve.
    - Cons:
        - Nested class structures can be harder to navigate as the number of events grows.
        - Lacks the separation provided by files.

3. Enum-Like Grouping (Flat but Tagged)
    - What: Use tags or an explicit enumeration to classify events while keeping them in a single file.
    - How:
        class EventCategory:
            WORKFLOW = "workflow"
            UI = "ui"

        class NodeReadyEvent(BaseEvent):
            category = EventCategory.WORKFLOW

            def __init__(self, payload: "BaseNode"):
                super().__init__(payload)

        class UserInteractionEvent(BaseEvent):
            category = EventCategory.UI

            def __init__(self, payload: "InteractionContext"):
                super().__init__(payload)
                

- Usage:

        if event.category == EventCategory.WORKFLOW:
            process_workflow_event(event)

    - Pros:
        - Simple to implement, no need to refactor imports or folder structure.
        - Useful for runtime classification of events.

    - Cons:
        - Doesn't provide as much structural separation or clarity during development
        - Grouping is implicit and relies on discipline.
        

4. Hybrid Approach
    - Combine Python Modules and Class Namespacing:
        - Use Python modules for major categories (e.g., Workflow, UI) and classes within modules for subcategories or grouping.

        Example Folder Structure:
            events/
                workflow.py
                ui.py
            
        - workflow.py

            class WorkflowEvents:
                class NodeReadyEvent(BaseEvent):
                    def __init__(self, payload: "BaseNode")
                        super().__init__(payload)

        - ui.py:

            class UIEvents:
                class UserInteractionEvent(BaseEvent):
                    def __init__(self, payload: "InteractionContext")
                        super().__init__(payload)

    - Usage:

            from events.workflow import WorkflowEvents
            from events.ui import UIEvents

            node_ready_event = WorkflowEvents.NodeReadyEvent(payload)

        - Pros:
            - Offers the best of both worlds: physical separation via modules and logical groupoing via classes.
            - Scales well for larger projects

        - Cons:
            - Slightly more boilerplate.

Recommendation
    - Start with Option 1: Python Modules if the event list grows across different categories (Workflow, UI, System).
    - Use Option 4: Hybrid Approach if you expect subcategories or more nuanced grouping in the future.

    Both approaches balance scalability and organization while keeping things manageable.


Categorizing events is primarily for readability and maintainability, but it can also provide indirect functional advantages
depending on how you implement event subscription and processing. Here's a deeper dive into the benefits and limitations of 
categorization:

Primary Benefits: Readability and Organization
1. Improved Discoverability:
    - Grouping related events makes it easier to locate specific events during development, especially in larger systems.
    - For example, all workflow-related events in workflow.py give a clear picture of what's happening in that domain.

2. Logical Separation:
    - Keeps different concerns (e.g., UI events, workflow events, system events) separate, making the system easier to 
    understand and debug.
    - Reduces cognitive overhead by avoiding a monolithic structure.

3. Scalability:
    - As the system grows, categorized events prevent bloated files and maintain structure, making refactoring easier.

4. Simplified Collaboration:
    - For teams, clear categorization provides a shared understanding of where to find and add new events.


Indirect Functional Advantages
While categorization itself doesn't inherently change functionality, it can:
1. Streamline Event Subscription:
    - If you categorize events, subscribers can selectively process events of a particular category rather than sifting through 
    all events.

    Example:
        - A subscriber only listens for workflow events:
        
            if instance(event, WorkflowEvents.NodeReadyEvents):
                handle_workflow_event(event)

2. Enable Filtering and Grouped Processing:
    - Event processors can apply filters based on event categories or namespaces, improving performance or simplifying logic.

    Example:
        - A centralized event processor could route events to specific handlers based on category:

            if event.category == EventCategory.WORKFLOW:
                workflow_handler.process(event)
            elif event.category == EventCategory.UI:
                ui_handler.process(event)

3. Improved Debugging and Logging:
    - Categorized events can improve logging and debugging by tagging logs or error messages with event types.
    
    Example log entry
"""