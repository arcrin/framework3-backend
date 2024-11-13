from _Node._BaseNode import BaseNode
from _Application._SystemEvent import TestRunTerminationEvent
from _Application._SystemEventBus import SystemEventBus
from util._InteractionContext import InteractionContext, InteractionType
from _Application._SystemEvent import UserInteractionEvent
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from _Application._DomainEntity._TestRun import TestRun
    from _Node._BaseNode import NodeState


class TestRunTerminalNode(BaseNode):
    def __init__(self, test_run: "TestRun"):
        super().__init__("TestRunTerminalNode")
        self._test_run = test_run
        self._logger = logging.getLogger("TestRunTerminalNode")

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value: "NodeState"):
        self._state = value

    async def execute(self):
        self._logger.info(f"Executing TestRunTerminalNode {self.id}")
        interaction_context = InteractionContext(InteractionType.Notification, "Test run completed")
        user_interaction_event = UserInteractionEvent(interaction_context)
        await SystemEventBus.publish(user_interaction_event)
        test_run_termination_event = TestRunTerminationEvent(
            {"tr_id": self._test_run.id}
        )  # type: ignore
        assert (
            self._test_run.parent_panel is not None
        ), "TestRunTerminalNode must be associated with a panel"
        self._test_run.parent_panel.remove_test_run()
        await SystemEventBus.publish(test_run_termination_event)

"""
Key Elements in TestRunTerminationNode
1. Node Initialization and Purpose:
    - This node is a terminal point in a test sequence, marking the ned of a test run. Its primary
    purpose is to send termination notifications and clean up resources related to the test run.
    - It takes a TestRun object as argument, allowing it to interact and modify test run state.
2. State Property:
    - The state property is implemented similarly to other nodes, using the parent BaseNode class's
    NodeState enum for consistency across nodes.
3. execute Method:
    - The execute method is responsible for finalizing the test run. Here's what it does step-by-step:
        - Logging: Logs execution for traceability.
        - User Interaction Event: Creates a notification using InteractionContext and triggers a 
        UserInteractionEvent to signal that the test run has completed. This may update the user 
        interface or notify the user.
        - Test Run Termination Event: Publishes a TestRunTerminationEvent, which could be used by other 
        parts of the system to perform any additional cleanup or logging associated with the test run.
        - Panel Association: It removes the test run from its parent panel, signaling that this test run
        is complete.
4. Assertions:
    - There's an assertion to ensure parent_panel is set in TestRun, helping catch configuration issues early.
    This assertion enforces that each test run is associated with a panel, which seems to be necessary for 
    resource cleanup
5. Event-Driven
    - This node leverages an event-driven design, using SystemEventBus.publish to dispatch both UserInteractionEvent
    and TestRunTerminationEvent. This aligns with the Producer-Consumer pattern you're using and decouples the terminal
    node from specific downstream listeners.

Considerations
1. Error Handling:
    - It might be worth considering error handling within execute, particularly around event publishing or removing the
    test run from the panel. If there's a failure in either operation, a fallback of logging mechanism could help identify
    issues.
2. Flexible Finalization:
    - If the finalization process for a test run could vary, consider parameterizing the TestRunTerminalNode or subclassing 
    it for different termination behavior. For instance, you might have different terminal nodes for "normal" completion 
    versus "failure" completion, each performing distinct tasks.
3. Dependencies on SystemEventBus and InteractionContext:
    - This node is tightly coupled to SystemEventBus and InteractionContext. If these components evolve, the node may need
    adjustments, so consider how changes in these dependencies would impact this node.
    

Reducing the coupling of TestRunTerminalNode with SystemEventBus and InteractionContext could enhance flexibility and make
the node more adaptable to changes in how events and interactions are handled. Here are a few strategies to decouple these
dependencies:
1. Introduce an Event Handler Interface.
    - define an interface or abstract base class for an event handler, which TestRunTerminalNode would rely on instead of 
    SystemEventBus directly.
    - You could inject an instance of this handler into TestRunTerminalNode at initialization, allowing for different 
    implementations without modifying the node itself.
    
        from abc import ABC, abstractmethod

        class EventPublisher(ABC):
            @abstractmethod
            async def publish(self, event: Any) -> None:
                pass
                
        class SystemEventPublisher(EventPublisher):
            async def publish(self, event: Any) -> None:
                await SystemEventBus.publish(event)

    Then, TestRunTerminalNode would receive an EventPublisher object:

        def __init__(self, test_run: "TestRun", event_publisher: EventPublisher):
            super().__init__("TestRunTerminalNode")
            self._test_run = test_run
            self._event_publisher = event_publisher

        asyn def execute(self):
            ...
            await self._event_publisher.publish(user_interaction_event)
            await self._event_publisher.publish(test_run_termination_event)

    Advantages:
        - Swappable event handling logic (e.g., use a different publisher in testing or for future enhancement).
        - Reduces dependency on SystemEventBus and keeps TestRunTerminalNode agnostic to event system details
        
2. Use a Factory for Creating Interaction Contexts
    - define a factory or builder for InteractionContext that TestRunTerminalNode can use to create interaction
    contexts without direct dependency.
    - This would allow TestRunTerminalNode to create interaction contexts in a more abbstracted way, where details 
    of context construction could change without impacting the node.

        class InteractionContextfactory:
            @staticmethod
            def create_notification(message: str) -> InteractionContext:
                return InteractionContext(InteractionType.Notification, message)

    Then, TestRunTerminalNode could call:

        interaction_context = InteractionContextFactory.create_notification("Test run completed")

    Advantages:
        - Isolates InteractionContext creation from the node's core logic.
        - Allows flexibility if you need  to modify the structure or creation of interaction contexts.
3. Combine with Dependency Injection (DI) for flexibility
    - With DI (using DI container or simple injection at instantiation), you could provide TestRunTerminalNode 
    with both the EventPublisher and InteractionContextFactory.
    - This way, the node would be fully decoupled from the specifics of the event bus and interaction context 
    and would instead rely on abstractions that can evolve independently.

        def __init__(
            self,
            test_run: "TestRun", 
            event_publisher: EventPublisher,
            interaction_context_factory: InteractionContextFactory
        ):
            super().__init__("TestRunTerminalNode")
            self._test_run = test_run
            self._event_publisher = event_publisher
            self._interaction_context_factory = interaction_context_factory

    This approach would make TestRunTerminalNode highly adaptable and minimize dependencies, making future 
    modifications to SystemEventBus or InteractionContext simpler and less disruptive.
"""