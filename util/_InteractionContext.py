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