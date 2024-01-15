from node.load_test_case_node import LoadTestCaseNode
from sample_profile.profile import SampleProfile
import unittest

class TestLoadTestCaseNode(unittest.TestCase):
  def test_execute(self):
    node_list = []
    profile_class = SampleProfile
    node = LoadTestCaseNode(node_list, profile_class)
    node.execute()
    self.assertEqual(len(node_list), 7)



if __name__ == '__main__':
  unittest.main()