from _Node._BaseNode import BaseNode
from _Application._SystemEvent import TestRunTerminationEvent


class TestRunTerminalNode(BaseNode):
  def __init__(self, test_run_id: str):
    super().__init__("TestRunTerminalNode")
    self._test_run_id = test_run_id 

  async def execute(self):
    assert self.event_bus is not None, "TestRunTerminalNode must be connected to an event bus"
    test_run_termination_event = TestRunTerminationEvent({"tr_id": self._test_run_id})
    await self.event_bus.publish(test_run_termination_event)