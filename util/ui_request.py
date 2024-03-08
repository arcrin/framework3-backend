# type: ignore
import trio

class UIRequestTask:
    def __init__(self) -> None:
        self._message = {
            "type": "prompt",
            "data": "int"
        }
        self.event = trio.Event()
        self._response = None

    @property
    def response(self):
        return self._response 
    
    @response.setter
    def response(self, value):
        self._response = value
        self.event.set()

    @property
    def message(self):
        return self._message    

class UIRequest():
    def __init__(self, send_channel) -> None:
        self._task = None  # a ws task that send the request to UI
        self._send_channel = send_channel   
        self._response = None

    @property
    def response(self):
        return self._response   
    
    @response.setter
    def response(self, value):  
        self._response = value

    async def queue_request(self) -> None:
        # TODO: queue the task that sends request to the UI
        task = UIRequestTask()
        await self._send_channel.send(task)
        await task.event.wait()
        self.response = task.response  

    