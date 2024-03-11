from typing import List, Dict, Any
import trio


class TCDataBroker:
    def __init__(self, send_channel: trio.MemorySendChannel[Dict[str, str]],
                 test_run_data: List[Any]) -> None:
        self._send_channel = send_channel
        self._test_run_data = test_run_data
        # TODO: properly annotate the data type
        self._tc_data: Dict[Any, Any] | None = None

    @property
    def tc_data(self) -> Dict[Any, Any] | None:
        return self._tc_data
    
    @tc_data.setter
    def tc_data(self, value: Dict[Any, Any]) -> None:
        self._tc_data = value

    async def update_test_case(self) -> None:
        self._test_run_data.append(self._tc_data)
        await self._queue_date()

    async def update_execution(self, execution_data): # type: ignore 
        self._tc_data["children"].append(execution_data) # type: ignore
        await self._queue_date()

    async def update_parameter(self, parameter_data: Dict[Any, Any]) -> None:
        self._tc_data["children"][-1]["children"].append(parameter_data) #type: ignore
        await self._queue_date()

    async def update_progress(self, progress_data: int) -> None:
        self._tc_data["data"]["progress"] = progress_data # type: ignore
        await self._queue_date()

    async def _queue_date(self) -> None:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self._send_channel.send, {"type": "tcData", "message": self._test_run_data}) # type: ignore

