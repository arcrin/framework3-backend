from node.executable_node import ExecutableNode
from sample_profile.scripts import task_func1, task_func2, task_func3,\
  task_func4, task_func5, task_func6, task_func7
from typing import List

class SampleProfile:
    def __init__(self) -> None:
        self._test_case_list: List[ExecutableNode] = []

        tc1 = ExecutableNode(task_func1)
        tc2 = ExecutableNode(task_func2)
        tc3 = ExecutableNode(task_func3)
        tc4 = ExecutableNode(task_func4)
        tc5 = ExecutableNode(task_func5)
        tc6 = ExecutableNode(task_func6)
        tc7 = ExecutableNode(task_func7)

        tc1.add_dependency(tc2)
        tc2.add_dependency(tc3)
        tc1.add_dependency(tc4)
        tc4.add_dependency(tc5)
        tc3.add_dependency(tc5)
        tc2.add_dependency(tc6)
        tc6.add_dependency(tc7) 

        self._test_case_list.append(tc1)
        self._test_case_list.append(tc2)
        self._test_case_list.append(tc3)
        self._test_case_list.append(tc4)
        self._test_case_list.append(tc5)
        self._test_case_list.append(tc6)
        self._test_case_list.append(tc7)

    @property
    def test_case_list(self) -> List[ExecutableNode]:
        return self._test_case_list

    def add_test(self, tc: ExecutableNode) -> None:
        self._test_case_list.append(tc)



    