from enum import Enum
from uuid import uuid4
from trio import Event



class InteractionType(Enum):
    InputRequest = "input_request"
    Notification = "notification"
    Decision = "decision"


class InteractionContext:
    def __init__(self, interaction_type: InteractionType, message: str):
        self._id = uuid4().hex
        self._interaction_type = interaction_type
        self._message = message
        self._response_ready_flag = Event()
        self._response = None

    @property
    def id(self):
        return self._id
    
    @property
    def message(self):
        return self._message
    
    @property
    def interaction_type(self):
        return self._interaction_type

    @property
    def response(self): # type: ignore
        return self._response # type: ignore
    
    @response.setter
    def response(self, value): # type: ignore
        self._response = value # type: ignore
        self._response_ready_flag.set()

    async def response_ready(self):
        await self._response_ready_flag.wait()


# TODO: add timeout to user interaction


"""
Key Elements of InteractionContext
1. Unique Identifier and Interaction Type:
    - Each InteractionContext has a unique ID (using uuid) and a specific interaction type (InteractionType enum).
    This setup ensures that each interaction is identifiable and categorized, making it easy to handle different
    types of interactions appropriately.
2. Event-Driven Synchronization:
    - The _response_ready_flag (Event) provides an elegant way to manage synchronous response handling. Any processor 
    waiting for a response can simply await response_ready(), which waits until the flag is set.
    - When a response is received, the response property's setter sets _response_ready_flag, signaling that the response
    is ready. This approach keeps synchronization internal to InteractionContext, simplifying external logic.
3. Flexible Response Storage:
    - The response itself is stored in _response and accessible through a property. This setup keeps the response 
    encapsulated, allowing other components to read or set it as needed.

Potential Enhancements
1. Timeout Handling:
    - Adding a timeout to response_ready() would help avoid indefinite waiting if a response is not received. This could
    be particularly useful if user input is expected but doesn't arrive within a reasonable timeframe.
    - Implementing a timeout might look like this:

        async def response_ready(self, timeout: float = None):
            try:
                with trio.fail_after(timeout):
                    await self._response_ready_flag.wait()
            except trio.TooSlowError:
                self._response = "Timeout"

2. Enhanced Response Type Handling:
    - If responses vary in structure depending on interaction_type, consider validating or structuring responses based on type.
    For example, you might add type-specific validation in the response setter.

3. Support for Optional Metadata:
    - You might add an optional metadata attribute, allowing additional data (e.g., timestamps or UI-related details) to be associated
    with the interaction. This could be helpful for UI components or logging.

4. Optional Logging or Debugging:
    - For traceability, adding optional logging in the response setter when a response is set can help track when responses are completed, 
    especially in complex workflows with multiple interactions.


Updated InteractionContext 

    class InteractionContext:
        def __init__(self, interaction_type: InteractionType, message: str):
            self._id = uuid4().hex
            self._interaction_type = interaction_type
            self._message = message
            self._response_ready_flag = Event()
            self._response = None
            ...

        async def response_ready(self, timeout: float = None):
            try:
                with trio.fail_after(timeout):
                    await self._response_ready_flag.wait()
            except trio.TooSlowError:
                self._response = "Timeout"
"""