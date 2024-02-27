from node.tc_node import TCNode
from sample_profile.scripts import task_func1, task_func3, fib
from functools import partial


async def test_tc_node_result():
    node = TCNode(task_func1)
    assert node.result is None
    await node.execute()
    assert node.result == 1

async def test_tc_node_with_async_executable():
    node = TCNode(task_func1)
    assert node.name == "task_func1"
    await node.execute()
    assert node.result == 1

async def test_tc_node_with_sync_executable():
    node = TCNode(partial(task_func3, 10), name="task_func3")
    assert node.name == "task_func3"
    await node.execute()
    assert node.result == fib(10)