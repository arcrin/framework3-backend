from typing import Callable, Dict, Any
import logging
import trio

class AppCommandProcessor:
    def __init__(
            self,
            command_receive_channel: trio.MemoryReceiveChannel[Dict[Any, Any]],
            command_mapping: Dict[str, Callable[..., Any]]) :
        self._command_receive_channel = command_receive_channel
        self._command_mapping = command_mapping
        self._logger = logging.getLogger("AppCommandProcessor")

    async def start(self):
        try:
            async for command in self._command_receive_channel:
                self._logger.info(f"Command received: {command["command_type"]}")
                if command["command_type"] in self._command_mapping:
                    await self._command_mapping[command["command_type"]](**command["payload"])
                else:
                    self._logger.info(f"Command {command} not found")
        except Exception as e:
            self._logger.error(e)
            raise


# TODO: Do I need to convert this into event based operation? Is there any scenario where I need to execute multiple commands at the same time?
# TODO: How about a command queue?
# TODO: what dictates the number of command can be executed at the same time?


"""
Key Elements in AppCommandProcessor
1. Command Mapping and Execution
    - AppCommandProcessor maintains a command_mapping dictionary that associates each command type with a corresponding  function.
    When a command is received, it checks the command_type against the mapping and invokes the function  if it exists.
    - This design makes it flexible and extensible, as you can easily add new commands by updating the command_mapping dictionary.

2. Channel-Based Command Reception:
    - Commands are received asynchronously via command_received_channel, which decouples AppCommandProcessor from the source of 
    commands, aligning with the producer-consumer model.

3. Logging:
    - It logs each command received and reports when a command type isn't found in the mapping, which is useful for debugging and 
    monitoring command flows.

Suggestions and Considerations
1. Convert to Event-Based Operation
    - If commands need to trigger events that other components listen to (like SystemEventBus), you might consider using an event-based system.
    - However, if the commands primarily involve direct actions or internal state changes, the current approach may be simpler and more efficient.

2. Implement a Command Queue
    - A command queue would be useful if you expect a high volume of commanders or want to control the order of execution, such as prioritizing 
    certain commands or processing them in batches.
    - Using a queue could also allow commands to be buffered if they arrive faster than they can be executed, preventing command overload.

3. Parallel Execution Control
    - If commands are independent of each other, consider processing multiple commands in parallel using Trio's nursery or by implementing a command
    semaphore to limit concurrency.
    - Factors Dictating Concurrency:
        - System Resources: Running multiple commands simultaneously can be CPU or memory-intensive, especially if commands involve I/O operations.
        - Command Dependencies: If some commands depend on the results of others, you may need to enforce sequential execution or set up dependencies
        between commands.
        
Example Updates with Command Queue and Concurrency Control:
    class AppCommandProcessor:
        def __init__(
            self,
            command_receive_channel: trio.MemoryReceiveChannel[Dict[Any, Any]],
            command_mapping: Dict[str, Callable[..., Any]],
            max_concurrent_commands: int = 5  # Set a default concurrency limit
        ):
            self._command_receive_channel = command_receive_channel
            self._command_mapping = command_mapping
            self._logger = logging.getLogger("AppCommandProcessor")
            self._semaphore = trio.Semaphore(max_concurrent_commands)

        async def _execute_command(self, command_type: str, payload: Dict[str, Any]):
            async with self._semaphore:
                if command_type in self._command_mapping:
                    await self._command_mapping[command_type](**payload)
                else:
                    self._logger.info(f"Command {command_type} not found in mapping")

        async def start(self):
            async with trio.open_nursery() as nursery:
                async for command in self._command_receive_channel:
                    self._logger.info(f"Command received: {command['command_type']}")
                    nursery.start_soon(
                        self._execute_command,
                        command["command_type"],
                        command["payload"]
                    )

                    
Addressing Your Specific Questions
- Event-Based Operation: Convert to event-based if commands need to trigger additional asynchronous workflows in other components. However, if commands
directly modify state or trigger isolated actions, the current approach may be preferable.
- Command Queue: Implement a command queue if command arrival rates vary significantly or you want to add prioritization or buffering.
- Concurrency Limits: Use a semaphore to limit concurrency if you expect multiple commands to run simultaneously. The max_concurrent_commands parameter
would allow you to adjust this limit based on system capacity.
"""