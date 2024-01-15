# type: ignore
from application import Application
from node.load_test_case_node import LoadTestCaseNode
import asyncio
import unittest



class TestApplication(unittest.IsolatedAsyncioTestCase):
  def test_application_init(self):
    app = Application()
    self.assertEqual(app.nodes, [])
    self.assertIsInstance(app._queue_for_executable_nodes, asyncio.Queue)
    self.assertTrue(app._queue_for_executable_nodes.empty())


  async def test_load_profile(self):
    app = Application()
    await app.load_test_case()
    self.assertTrue(isinstance(await app._queue_for_executable_nodes.get(), LoadTestCaseNode))

    
if __name__ == "__main__":
  unittest.main()