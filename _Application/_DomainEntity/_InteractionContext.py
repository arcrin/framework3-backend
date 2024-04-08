from enum import Enum, auto
from typing import Dict, Any
from uuid import uuid4
from trio import Event



class InteractionType(Enum):
    InputRequest = auto()
    Notification = auto()
    Decision = auto()


class InteractionContext:
    def __init__(self, interaction_type: InteractionType, payload: Dict[str, Any]):
        self._id = uuid4().hex
        self._interaction_type = interaction_type
        self._payload = payload
        self._response_ready_flag = Event()
        self._response = None

    @property
    def id(self):
        return self._id

    @property
    def response(self): # type: ignore
        return self._response # type: ignore
    
    @response.setter
    def response(self, value): # type: ignore
        self._response = value # type: ignore
        self._response_ready_flag.set()

    async def response_ready(self):
        await self._response_ready_flag.wait()