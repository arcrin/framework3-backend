from node.base_node import BaseNode

class SentinelNode(BaseNode):
  def __init__(self):
    super().__init__("SentinelNode")
  
  async def execute(self):
    pass

  @property
  def result(self):
    return None