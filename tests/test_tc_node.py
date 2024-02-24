from node.tc_node import TCNode
from sample_profile.scripts import task_func1


async def test_executable_node_result():
    node = TCNode(task_func1)
    assert node.result is None
    await node.execute()
    assert node.result is True


async def test_executable_node_with_async_executable():
    node = TCNode(task_func1)
    assert node.name == "task_func1"
    await node.execute()
    assert node.result == 1