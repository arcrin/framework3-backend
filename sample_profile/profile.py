# type: ignore
from _Application._DomainEntity._TestCaseDataModel import TestCaseDataModel
from _Application._DomainEntity._Parameter import SingleValueParameter
from _Node._BaseNode import BaseNode
from util.dag_vis import draw_graph
from _Node._TCNode import TCNode
from typing import List
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


def sync_task1(data_model: TestCaseDataModel = None):
    assert data_model is not None, "Must have a data model"
    logger.info("Start sync task1")

    parameter = SingleValueParameter("parameter1")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 100)
    return True


def sync_task2(data_model: TestCaseDataModel = None):
    assert data_model is not None, "Must have a data model"
    logger.info("Start sync task2")

    parameter = SingleValueParameter("parameter1")
    parameter.start_measurement("expected")
    time.sleep(2)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 100)
    return True


def sync_task3(data_model: TestCaseDataModel = None):
    assert data_model is not None, "Must have a data model"
    logger.info("Start sync task3")

    parameter = SingleValueParameter("parameter1")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 33)

    parameter = SingleValueParameter("parameter2")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 66)

    parameter = SingleValueParameter("parameter3")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 100)
    return 3


def sync_task4(data_model: TestCaseDataModel = None):
    assert data_model is not None, "Must have a data model"
    logger.info("Start sync task4")
    parameter = SingleValueParameter("parameter1")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 10)

    parameter = SingleValueParameter("parameter2")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 20)

    parameter = SingleValueParameter("parameter3")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 30)

    parameter = SingleValueParameter("parameter4")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 40)

    parameter = SingleValueParameter("parameter5")
    parameter.start_measurement("expected")
    time.sleep(3)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 70)

    parameter = SingleValueParameter("parameter6")
    parameter.start_measurement("expected")
    time.sleep(2)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 90)

    parameter = SingleValueParameter("parameter7")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 100)

    return True


def sync_task5(data_model: TestCaseDataModel = None):
    assert data_model is not None, "Must have a data model"
    logger.info("Start sync task5")

    parameter = SingleValueParameter("parameter1")
    parameter.start_measurement("expected")
    time.sleep(2)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 40)

    parameter = SingleValueParameter("parameter2")
    parameter.start_measurement("expected")
    time.sleep(3)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 100)
    return True


def sync_task6(data_model: TestCaseDataModel = None):
    assert data_model is not None, "Must have a data model"
    logger.info("Start sync task6")

    parameter = SingleValueParameter("parameter1")
    parameter.start_measurement("expected")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 16)

    parameter = SingleValueParameter("parameter2")
    parameter.start_measurement("expected")
    time.sleep(3)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 65)

    parameter = SingleValueParameter("parameter3")
    parameter.start_measurement("expected")
    time.sleep(2)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 100)
    return True


def sync_task7(data_model: TestCaseDataModel = None, tc6=None):
    over_all_result = True
    assert data_model is not None, "Must have a data model"
    logger.info("Start sync task7")

    parameter = SingleValueParameter("parameter1")
    parameter.start_measurement("1")
    # TODO: Need to handle user input cancel action
    # TODO: replace UI Request with interaction context
    # trio.from_thread.run(ui_request.queue_request)
    # parameter.stop_measurement(
    #     ui_request.response, "User input verification", ui_request.response == "1"
    # )

    # logger.info(f"task7 parameter 1 response: {ui_request.response}")
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 10)
    # TODO: replace UI Request with interaction context
    # if ui_request.response != "1":
    #     over_all_result = False
    #     return over_all_result

    parameter = SingleValueParameter("parameter2")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 20)

    parameter = SingleValueParameter("parameter3")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 30)

    parameter = SingleValueParameter("parameter4")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 40)

    parameter = SingleValueParameter("parameter5")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 50)

    parameter = SingleValueParameter("parameter6")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 60)

    parameter = SingleValueParameter("parameter7")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 70)

    parameter = SingleValueParameter("parameter8")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 80)

    parameter = SingleValueParameter("parameter9")
    parameter.start_measurement("expected")
    time.sleep(1)
    parameter.measured_value = "measured"
    parameter.stop_measurement("measured", "description", True)
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 90)

    parameter = SingleValueParameter("parameter10")
    parameter.start_measurement("expected")
    # TODO: Need to handle user input cancel action
    # TODO: Replace UI Request with interaction context
    # trio.from_thread.run(ui_request.queue_request)
    # parameter.stop_measurement(ui_request.response, "description", True)
    # logger.info(f"task7 response: {ui_request.response}")
    trio.from_thread.run(data_model.update_parameter, parameter)
    trio.from_thread.run(data_model.update_progress, 100)
    return True


if __name__ == "__main__":
    sample_profile = SampleTestProfile()
    draw_graph(sample_profile.test_case_list[0])
