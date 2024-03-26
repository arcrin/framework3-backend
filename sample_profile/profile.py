# type: ignore
from _Node._BaseNode import BaseNode
from util.dag_vis import draw_graph
from _Node._TCNode import TCNode
from typing import List
from util.ui_request import UIRequest
from util.tc_data_broker import TCDataBroker
import trio
import time
import logging

logger = logging.getLogger("Script")


class SampleTestProfile:
    def __init__(self) -> None:
        self._test_case_list: List[BaseNode] = []

        # terminal_node = TerminalNode()

        tc1 = TCNode(sync_task1, "Test Case 1")
        tc2 = TCNode(sync_task2, "Test Case 2")
        tc3 = TCNode(sync_task3, "Test Case 3")
        tc4 = TCNode(sync_task4, "Test Case 4")
        tc5 = TCNode(sync_task5, "Test Case 5")
        tc6 = TCNode(sync_task6, "Test Case 6")
        tc7 = TCNode(sync_task7, "Test Case 7", "tc7")

        tc1.add_dependency(tc2)
        tc2.add_dependency(tc3)
        tc1.add_dependency(tc4)
        tc4.add_dependency(tc5)
        tc3.add_dependency(tc5)
        tc2.add_dependency(tc6)
        tc6.add_dependency(tc7)

        # terminal_node.add_dependency(tc1)

        self._test_case_list.append(tc1)
        self._test_case_list.append(tc2)
        self._test_case_list.append(tc3)
        self._test_case_list.append(tc4)
        self._test_case_list.append(tc5)
        self._test_case_list.append(tc6)
        self._test_case_list.append(tc7)
        # self._test_case_list.append(terminal_node)

    @property
    def test_case_list(self) -> List[BaseNode]:
        return self._test_case_list

    def add_test(self, tc: TCNode) -> None:
        self._test_case_list.append(tc)


def fib(n: int) -> int:
    if n <= 1:
        return n
    else:
        return fib(n - 1) + fib(n - 2)


def sync_task1():  # type: ignore
    logger.info("Start sync task1")
    time.sleep(1)
    return 1


def sync_task2():
    logger.info("Start sync task2")
    time.sleep(2)
    return 2


def sync_task3():
    logger.info("Start sync task3")
    time.sleep(1)
    time.sleep(1)
    time.sleep(1)
    return 3


def sync_task4():
    logger.info("Start sync task4")
    time.sleep(1)
    time.sleep(1)
    time.sleep(1)
    time.sleep(1)
    return True


def sync_task5():
    logger.info("Start sync task5")
    time.sleep(2)
    time.sleep(3)
    return True


def sync_task6():  # type: ignore
    logger.info("Start sync task6")
    time.sleep(1)
    time.sleep(3)
    time.sleep(2)
    return True


def sync_task7(ui_request: UIRequest = None, tc6=None):
    logger.info("Start sync task7")
    time.sleep(1)

    # trio.from_thread.run(
    #     tc_data_broker.update_parameter,
    #     {
    #         "key": "parameter1",
    #         "data": {
    #             "name": "parameter1",
    #             "expected": "expected",
    #             "measured": "measured",
    #             "description": "Description 1",
    #         },
    #     },
    # )
    # trio.from_thread.run(tc_data_broker.update_progress, 10)
    time.sleep(1)
    # trio.from_thread.run(
    #     tc_data_broker.update_parameter,
    #     {
    #         "key": "parameter2",
    #         "data": {
    #             "name": "parameter2",
    #             "expected": "expected",
    #             "measured": "measured",
    #             "description": "Description 2",
    #         },
    #     },
    # )
    # trio.from_thread.run(tc_data_broker.update_progress, 20)
    time.sleep(1)
    # trio.from_thread.run(
    #     tc_data_broker.update_parameter,
    #     {
    #         "key": "parameter3",
    #         "data": {
    #             "name": "parameter3",
    #             "expected": "expected",
    #             "measured": "measured",
    #             "description": "Description 3",
    #         },
    #     },
    # )
    # trio.from_thread.run(tc_data_broker.update_progress, 30)
    time.sleep(1)
    # trio.from_thread.run(
    #     tc_data_broker.update_parameter,
    #     {
    #         "key": "parameter4",
    #         "data": {
    #             "name": "parameter4",
    #             "expected": "expected",
    #             "measured": "measured",
    #             "description": "Description 4",
    #         },
    #     },
    # )
    # trio.from_thread.run(tc_data_broker.update_progress, 40)
    time.sleep(1)
    # trio.from_thread.run(
    #     tc_data_broker.update_parameter,
    #     {
    #         "key": "parameter5",
    #         "data": {
    #             "name": "parameter5",
    #             "expected": "expected",
    #             "measured": "measured",
    #             "description": "Description 5",
    #         },
    #     },
    # )
    # trio.from_thread.run(tc_data_broker.update_progress, 50)
    time.sleep(1)
    # trio.from_thread.run(
    #     tc_data_broker.update_parameter,
    #     {
    #         "key": "parameter6",
    #         "data": {
    #             "name": "parameter6",
    #             "expected": "expected",
    #             "measured": "measured",
    #             "description": "Description 6",
    #         },
    #     },
    # )
    # trio.from_thread.run(tc_data_broker.update_progress, 60)
    time.sleep(1)
    # trio.from_thread.run(
    #     tc_data_broker.update_parameter,
    #     {
    #         "key": "parameter7",
    #         "data": {
    #             "name": "parameter7",
    #             "expected": "expected",
    #             "measured": "measured",
    #             "description": "Description 7",
    #         },
    #     },
    # )
    # trio.from_thread.run(tc_data_broker.update_progress, 70)
    time.sleep(1)
    # trio.from_thread.run(
    #     tc_data_broker.update_parameter,
    #     {
    #         "key": "parameter8",
    #         "data": {
    #             "name": "parameter8",
    #             "expected": "expected",
    #             "measured": "measured",
    #             "description": "Description 8",
    #         },
    #     },
    # )
    # trio.from_thread.run(tc_data_broker.update_progress, 80)
    time.sleep(1)
    # trio.from_thread.run(
    #     tc_data_broker.update_parameter,
    #     {
    #         "key": "parameter9",
    #         "data": {
    #             "name": "parameter9",
    #             "expected": "expected",
    #             "measured": "measured",
    #             "description": "Description 9",
    #         },
    #     },
    # )
    # trio.from_thread.run(tc_data_broker.update_progress, 90)
    time.sleep(1)

    # TODO: Need to handle user input cancel action
    trio.from_thread.run(ui_request.queue_request)
    # trio.from_thread.run(
    #     tc_data_broker.update_parameter,
    #     {
    #         "key": "user_input",
    #         "data": {
    #             "name": "User Input",
    #             "expected": 123,
    #             "measured": ui_request.response,
    #             "description": "User input verification",
    #         },
    #     },
    # )
    logger.info(f"task7 response: {ui_request.response}")  # type: ignore
    # trio.from_thread.run(tc_data_broker.update_progress, 100)
    return True


if __name__ == "__main__":
    sample_profile = SampleTestProfile()
    draw_graph(sample_profile.test_case_list[0])
