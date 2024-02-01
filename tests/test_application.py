# type: ignore
from application import Application
from node.load_test_case_node import LoadTCNode
import asyncio
import unittest



class TestApplication(unittest.IsolatedAsyncioTestCase):
  def test_application_init(self):
    app = Application()
    self.assertEqual(app.nodes, [])
    self.assertIsInstance(app._queue_for_execution, asyncio.Queue)
    self.assertTrue(app._queue_for_execution.empty())


  async def test_load_profile(self):
    app = Application()
    await app.load_test_case()
    self.assertEqual(len(app._nodes), 8) # sample profile has 8 test cases, including the sentinel node

    
if __name__ == "__main__":
  unittest.main()