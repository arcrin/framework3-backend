from node.load_test_case_node import LoadTCNode
from sample_profile.profile import SampleTestProfile
import unittest

class TestLoadTCNode(unittest.IsolatedAsyncioTestCase):
  async def test_execute(self):
    node_list = []
    profile_class = SampleTestProfile
    node = LoadTCNode(node_list, profile_class)
    await node.execute()
    self.assertEqual(len(node_list), 8)



if __name__ == '__main__':
  unittest.main()