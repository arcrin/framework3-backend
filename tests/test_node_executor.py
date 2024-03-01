# type: ignore
from producer_consumer.node_executor import NodeExecutor
from node.base_node import BaseNode
import trio
import trio.testing
import pytest



node_executor_send_channel, node_executor_receive_channel = trio.open_memory_channel(50)
result_processor_send_channel, result_processor_receive_channel = trio.open_memory_channel(50)


@pytest.mark.trio
async def test_execute_node(mocker):
    node_executor = NodeExecutor(node_executor_receive_channel, result_processor_send_channel)
    mock_node = mocker.Mock(spec=BaseNode)
    mock_node.name = "MockNode"

    await node_executor._execute_node(mock_node)

    mock_node.execute.assert_called_once()

    sent_node = await result_processor_receive_channel.receive()

    assert sent_node == mock_node

@pytest.mark.trio
async def test_execute_node_with_exception(mocker):
    node_executor = NodeExecutor(node_executor_receive_channel, result_processor_send_channel)
    mock_node = mocker.Mock(spec=BaseNode)
    mock_node.name = "MockNode"

    mock_node.execute.side_effect = ValueError("An error occurred")

    with pytest.raises(ValueError) as exc:
        await node_executor._execute_node(mock_node)

    assert str(exc.value) == "An error occurred"

    mock_node.execute.assert_called_once()


@pytest.mark.trio
async def test_process_receive_channel(mocker):
    node_executor = NodeExecutor(node_executor_receive_channel, result_processor_send_channel)

    mock_node = mocker.Mock(spec=BaseNode)
    mock_node.name = "MockNode"

    mocker.patch.object(NodeExecutor, "_execute_node", return_value=None)
    
    with node_executor_send_channel:
        await node_executor_send_channel.send(mock_node)

    await node_executor.start()

    NodeExecutor._execute_node.assert_called_once_with(mock_node)