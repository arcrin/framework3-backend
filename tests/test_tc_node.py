from _Node._TCNode import TCNode
from sample_profile.scripts import fib, sync_task1, sync_task2, sync_task3, async_task1, async_task2, async_task3
from functools import partial
import pytest


async def sample_test_case():
    raise ValueError("Value error in sample test case")


def test_func_parameter_label():
    node = TCNode(sync_task1, name="Test Case 1")
    with pytest.raises(ValueError):
        node.func_parameter_label

    node = TCNode(sync_task1, 
                  name="Test Case 1", 
                  func_parameter_label="task1_parameter")
    assert node.func_parameter_label == "task1_parameter"

async def test_tc_node_result():
    node = TCNode(async_task1, "Test Case")
    assert node.result is None
    await node.execute()
    assert node.result == 1

async def test_tc_node_with_async_executable():
    node = TCNode(async_task1, "Test Case")
    assert node.name == "Test Case"
    await node.execute()
    assert node.result == 1

async def test_tc_node_with_sync_executable():
    node = TCNode(partial(fib, 10), name="task_func3")
    assert node.name == "task_func3"
    await node.execute()
    assert node.result == 55

async def test_tc_node_execute_with_error():
    node = TCNode(sample_test_case, "Test Case")
    await node.execute()
    assert isinstance(node.error, ValueError)
    assert str(node.error) == "Value error in sample test case"
    print(node.error_traceback)

async def test_parameter_passing_for_sync_task():
    node1 = TCNode(sync_task1, name="Test Case 1", func_parameter_label="task1_parameter")
    node2 = TCNode(sync_task2, name="Test Case 2", func_parameter_label="task2_parameter")
    node3 = TCNode(sync_task3, name="Test Case 3", func_parameter_label="task3_parameter")

    node3.add_dependency(node1)
    node3.add_dependency(node2)

    await node1.execute()
    await node2.execute()

    await node3.execute()
    assert node3.result == 3


async def test_parameter_passing_for_async_task():
    node1 = TCNode(async_task1, name="Test Case 1", func_parameter_label="task1_parameter")
    node2 = TCNode(async_task2, name="Test Case 2", func_parameter_label="task2_parameter")
    node3 = TCNode(async_task3, name="Test Case 3", func_parameter_label="task3_parameter")

    node3.add_dependency(node1)
    node3.add_dependency(node2)

    await node1.execute()
    await node2.execute()

    await node3.execute()
    assert node3.result == 3