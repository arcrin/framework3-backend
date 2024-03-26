from _Node._BaseNode import BaseNode

class TerminalNode(BaseNode):
  def __init__(self):
    super().__init__("TerminalNode")
  
  async def execute(self):
    pass