from node.tc_node import TCNode
from node.tj_config_node import TJConfigNode
from node.product_info_node import ProductInfoNode
from node.load_profile_node import LoadProfileNode
from sample_profile.scripts import task_func1, task_func3
import asyncio
import unittest


class TestExecutableNode(unittest.IsolatedAsyncioTestCase):
  async def test_executable_node_result(self):
    node = TCNode(task_func1)
    self.assertEqual(node.result, None)
    await node.execute()
    self.assertEqual(node.result, True)

  async def test_executable_node_with_async_executable(self):
    node = TCNode(task_func1)
    self.assertEqual(node.name, "task_func1")
    await node.execute()
    self.assertEqual(node.result, True)

  async def test_executable_node_with_sync_executable(self):
    node = TCNode(task_func3)
    self.assertEqual(node.name, "task_func3")
    await node.execute()
    self.assertEqual(node.result, 55)

class TestTJConfigNode(unittest.IsolatedAsyncioTestCase):
  async def test_tj_config_node_init(self):
    async def tj_config_func():
      await asyncio.sleep(1)
      return {"tj_config": True}
    node = TJConfigNode(tj_config_func)
    await node.execute()
    self.assertEqual(node.result, {"tj_config": True})


class TestProductInfoNode(unittest.IsolatedAsyncioTestCase):
  async def test_product_info_node_init(self):
    async def product_info_func():
      await asyncio.sleep(1)
      return {"product_info": True}
    node = ProductInfoNode(product_info_func)
    await node.execute()
    self.assertEqual(node.result, {"product_info": True}) 


class TestLoadProfileNode(unittest.IsolatedAsyncioTestCase):
  async def test_load_profile_node_init(self):
    async def load_profile_func():
      await asyncio.sleep(1)
      return {"load_profile": True}
    node = LoadProfileNode(load_profile_func)
    await node.execute()
    self.assertEqual(node.result, {"load_profile": True})


if __name__ == "__main__":
  unittest.main()