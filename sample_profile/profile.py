from node.base_node import BaseNode
from node.terminal_node import TerminalNode
from util.dag_vis import draw_graph
from node.tc_node import TCNode
from typing import List
import time
import logging

logger = logging.getLogger("Script")

class SampleTestProfile:
    def __init__(self) -> None:
        self._test_case_list: List[BaseNode] = []

        terminal_node = TerminalNode()

        tc1 = TCNode(sync_task1, "Test Case 1")
        tc2 = TCNode(sync_task2, "Test Case 2")
        tc3 = TCNode(sync_task3, "Test Case 3")
        tc4 = TCNode(sync_task4, "Test Case 4")
        tc5 = TCNode(sync_task5, "Test Case 5")
        tc6 = TCNode(sync_task6, "Test Case 6")
        tc7 = TCNode(sync_task7, "Test Case 7")
        
        tc1.add_dependency(tc2)
        tc2.add_dependency(tc3)
        tc1.add_dependency(tc4)
        tc4.add_dependency(tc5)
        tc3.add_dependency(tc5)
        tc2.add_dependency(tc6)
        tc6.add_dependency(tc7) 
        
        terminal_node.add_dependency(tc1)

        self._test_case_list.append(tc1)
        self._test_case_list.append(tc2)
        self._test_case_list.append(tc3)
        self._test_case_list.append(tc4)
        self._test_case_list.append(tc5)
        self._test_case_list.append(tc6)
        self._test_case_list.append(tc7)
        self._test_case_list.append(terminal_node)


    @property
    def test_case_list(self) -> List[BaseNode]:
        return self._test_case_list

    def add_test(self, tc: TCNode) -> None:
        self._test_case_list.append(tc)



def fib(n: int) -> int:
    if n <= 1:
        return n
    else:
        return (fib(n-1) + fib(n-2))

def sync_task1():
    logger.info("Start sync task1")
    time.sleep(1)
    return 1

def sync_task2():
    logger.info("Start sync task2")
    time.sleep(2)
    return 2

def sync_task3():
    logger.info("Start sync task3")
    time.sleep(3)
    return 3

def sync_task4():
    logger.info("Start sync task4")
    time.sleep(4)
    return True

def sync_task5():
    logger.info("Start sync task5")
    time.sleep(5)
    return True

def sync_task6():
    logger.info("Start sync task6")
    time.sleep(6)
    return True

def sync_task7():
    logger.info("Start sync task7")
    time.sleep(7)
    return True


if __name__ == "__main__":
    sample_profile = SampleTestProfile()
    draw_graph(sample_profile.test_case_list[0])