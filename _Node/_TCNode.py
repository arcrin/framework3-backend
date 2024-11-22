from _Application._DomainEntity._TestCaseDataModel import TestCaseDataModel
from typing import Callable, Any
from _Application._SystemEvent import TestCaseFailEvent
from _Application._SystemEventBus import SystemEventBus
from util.async_timing import async_timed
from _Node._BaseNode import BaseNode, NodeState
from functools import partial
import traceback
import logging
import inspect
import trio
import sys


class TCNode(BaseNode):
    """
    A wrapper around test cases.
    """

    def __init__(
        self,
        callable_object: Callable[..., Any],
        name: str,
        # TODO: func_parameter_label is not the best way to handle dependencies. Replace it with a structured approach
        func_parameter_label: str | None = None,
        description: str = "",
    ) -> None:
        super().__init__(name=name, func_parameter_label=func_parameter_label)
        self._data_model = TestCaseDataModel(self._id, self._name, description)
        self._callable_object = callable_object
        self.execute = async_timed(self.name)(self.execute)
        self._logger = logging.getLogger("TCNode")
        self._logger.info(f"TCNode {self.id} created")
        self._auto_retry_count: int = 1
        self._data_model.state = NodeState.NOT_PROCESSED


    @property
    def state(self) -> NodeState:
        return self._data_model.state
    
    @state.setter
    def state(self, value: NodeState) -> None:
        self._data_model.state = value

    @property
    def auto_retry_count(self) -> int:
        return self._auto_retry_count

    @property
    def data_model(self) -> TestCaseDataModel:
        return self._data_model
    
    async def quarantine(self) -> None:
        assert self._data_model.parent_test_run is not None, "TCNode must be associated with a test run"
        self._data_model.parent_test_run.add_to_failed_test_cases(self)
        self.mark_as_failed()
        test_case_failed_event = TestCaseFailEvent({"tc_id": self.id})
        await SystemEventBus.publish(test_case_failed_event) # TODO: I should move it into TestCaseDataModel

    async def execute(self):
        self.mark_as_processing()
        await self.data_model.add_execution()
        # TODO: should put retry counts in the log
        self._auto_retry_count -= self.data_model.current_execution.execution_id
        assert (
            self.data_model.parent_test_run is not None
        ), "TCNode must be associated with a test run"

        try:
            # TODO: Update unit test to cover function signature check
            func_parameters = {}
            dependency_parameter_labels = [ d.func_parameter_label for d in self.dependencies 
                                           if d.func_parameter_label is not None]  # type: ignore 
            # Find out all parameter needed to execute test case 
            for p_name, p_obj in inspect.signature( self._callable_object).parameters.items():
                if p_obj.annotation is TestCaseDataModel:
                    func_parameters[p_name] = self.data_model
                else:
                    if p_name in dependency_parameter_labels:
                        for d in self.dependencies:
                            if d.func_parameter_label == p_name:
                                func_parameters[p_name] = d.result

            if inspect.iscoroutinefunction(self._callable_object):
                # Execute coroutine
                self._logger.info("Executing coroutine")
                async with trio.open_nursery() as nursery:  # type: ignore
                    self._result = await self._callable_object(**func_parameters)
            else:
                # Execute synchronous function
                self._logger.info("Executing synchronous function")
                async with trio.open_nursery() as nursery:  # type: ignore
                    self._result = await trio.to_thread.run_sync(
                        partial(self._callable_object, **func_parameters)
                    )  # type: ignore
        except Exception as e:
            self.error = e
            _, _, tb = sys.exc_info()
            frames = traceback.extract_tb(tb)
            frame_info = "\n".join(
                f"Frame {i}:\nFile {frames[i].filename}, "
                "line {frames[i].lineno}, "
                "in {frames[i].name}\n  {frames[i].line}"
                for i in range(len(frames))
            )
            self.error_traceback = traceback.format_exc() + "\n" + frame_info
            self._logger.error(f"Error while executing {self.name}: {e}", exc_info=True)

"""
Key Elements in TCNode
1. Integration with TestCaseDataModel:
    - Each TCNode maintains a TestCaseDataModel instance, representing the test case's data and state,
    which allows easy tracking of execution details and state management.
    - The state of the node is synchronized wih this data model.
2. Callable Object Handling:
    - TCNode accepts callable_object (likely the test function or coroutine) to execute. 
    - Using inspect to examine the callable's parameters is a thoughtful approach, ensuring
    that the node can dynamically inject dependency results and other needed parameters,
    such as the TestCaseDataModel
3. Parameter Injection:
    - Parameters are set up based on dependency results. By inspecting dependencies' func_parameter_label
    values, TCNode can pass results from upstream nodes to the callable, enabling data flow along the DAG
    structure.
    - This approach allow flexible and reusable test case functions that automatically receive dependecies' 
    outputs.
4. Retry Mechanism:
    - auto_retry_count provides a basic retry count, which is decremented based on the execution_id in 
    TestCaseDataModel. This approach might suppn auto-retry mechanism in the future.
    - If more advanced retry logic is needed, auto_retry_count could be enhanced or factored into a retry
    handler component.
5. Execution Management:
    - The execute method handles both synchronous and asynchronous functions, leveraging Trio's open_onursery 
    and to_thread.run_sync for concurrency. This approach allows seamless execution of both types of functions, 
    enhancing flexibility.
    - Execution errors are caught and stored in error and error_traceback, providing detailed information for 
    debugging.
6. Quarantine Mechanism:
    - The quarantine method moves failed test cases into a quarantine by generating a TestCaseFailEvent. This 
    mechanism allows the system to handle failures efficiently, potentially isolating problematic tests for 
    further review.

Potential Considerations
- Handling Dependencies in execute:
    - Currently, the function handles dependencies using a parameter name match based on func_parameter_label.
    This is effective but could potentially becom complex as dependecies grow. You might consider whether an 
    alternate, structured way to mange dependencies could reduce potential misconfigurations.
- Structured Logging for Retry:
    - Including specific log messages related to retries within the execute method, possibly with more granular
    information about execution_id and auto_retry_count, might make debugging and monitoring retries easier 
- Error Traceback Generation:
    - Generating detailed error traceback with frame-level info is a good approach; however, the formatting logic
    may be simplified if needed using Python's standard traceback formatting tools.
    

A structured approach to managing dependencies could simplify how TCNode retrieves and injects dependencies into
the test case callable, especially as the number of dependencies and complexity of parameters passing grows. Here
are some methods that might make dependency management more robust and modular.

1. Dependency Injection Container
    - Concept: Use a Dependency Injection Container to manage dependencies. In this approach, each node could 
    register its output in the central DI Container that any downstream node can query.
    
    - Implementation:
        - Upon completing execution, each node register its results in the DI container with a unique ID 
        (such as the node's ID or a label)
        - Nodes needing these results retrieve them directly from the DI container rather than relying on 
        the positional matching of func_parameter_label
    
    - Advantage:
        - Reduces the need for parameter name matching
        - Promotes flexibility, as nodes don't need to know the exact names of upstream dependencies, 
        only their identifiers in the DI container

    - Drawback: Adds a central dependency repository, which may require careful management and cleanup.
    
    The Dependency Injection (DI) container in this system could function as a centralized repository for
    dependencies, accessible across nodes without tightly coupling them. Here's a practical approach to 
    implementing and locating this container within the application.
        1. Location of the DI Container
            - The container should ideally be a singleton within the scope of the system to ensure all
            nodes can access a consistent set of dependencies.
            - It could be managed as part of a dedicated service or module within the application, such
            as DependencyRegistry or DependencyContainer.
        2. Implementation of the DI Container
            - The DI container can be a class with methods to register and retrieve dependencies, stroing
            dependencies in a dictionary-like structure.
        3. Integrating the DI Container with Nodes
            - Each BaseNode (or TCNode specifically) could register its result with the container after
            completing its task.
            - In TCNode, during the execute method, you would register the result after execution
            - When a node needs a dependency, it would retrieve it from the DependencyContainer rather than
            relying on the func_parameter_label
        4. Clearing Dependencies
            - After a test run or workflow completes, the container can be cleared using DependencyCOntainer.clear() 
            to prevent stale data from affecting subsequent runs.
            - Optionally, nodes themselves could unregister from the container after they finish their purpose, though
            this is not always necessary if a clear operation occurs between runs.
        5. Advantages
            - Modularity: Components access only the DI container, not each other, making dependencies modular and decoupled.
            - Flexibility: Nodes don't need to know details about upstream nodes; they only know what they need to retrieve by ID
            - Scalability: As the number of nodes grows, this pattern scales without increasing complexity in each node's implementation.
    
2. Dependency Resolution Map
    - Concept: Each TCNode maintains an explicit map of dependencies, listing each dependency and how it 
    maps to the parameters in the callable.
    - Implementation: 
        - TCNode could have an attribute dependency_map, where each dependency's output is mapped
        a specific parameter in the callable. This map would define both the dependency node ID and the corresponding 
        parameter name.
        - During execution, TCNode checks dependency_map to fetch each dependency's result and assign it to the correct 
        parameter in the callable.
    - Advantages:
        - Improves readability by explicitly mapping dependencies.
        - Makes dependencies more visible and manageable, as there's clear definition of which outputs go where.
    - Drawback: 
        - Requires manual setup of dependency_map for each node, which could become cumbersome for a large number of nodes.    

3. Typed Dependency Management with Decorator or Wrappers
    - Concept: Use decorators or helper functions to automatically inject dependencies based on type hints, leveraging 
    Python's type annotations to infer which dependencies a function needs.
    - Implementation:
        - Define a decorator (e.g., @inject_dependencies) that wraps the callable. This decorator inspects the function's
        type hints and automatically injects dependencies if they match the types of the available upstream node results.
        - Dependencies could be registered with specific types or classes, and the decorator would fetch and inject only 
        matching types.
    - Advantages:
        - Automates dependency injection based on types, reducing boilerplate code in each node
        - Improves type safety, making it clearer which dependencies a callable expects.
    - Drawback: This approach requires consistent type annotations across all callable and dependencies, which can become 
    restrictive.
    

Points to Align with Hierarchical Composition
1. Remove References to Higher Levels
    - TCNode currently has direct interactions with its TestRun via data_model.parent_test_run.
    - Since higher-level components should manage states independently, consider removing this reference
    - Instead, TCNode can publish events to the SystemEventBus (e.g., a TestCaseCompletedEvent) for the TestRun to handle.
2. Expose States via @property
    - Instead of relying on interactions with higher-level components, ensure that all necessary states and results are exposed via
    @property.
3. Centralize Quarantine and Retry Logic
    - Quarantine and retry logic might be better handled at the TestRun level, allowing TCNode to remain focused on
    individual test case execution.
    

TestCaseDataModel's role in TCNode
Purpose of TestCaseDataModel in TCNode

1. Data Representation:
    - Encapsulates metadata and state for a test case, such as its ID, name, description, and execution results.
    - Provides a structured way to store and retrieve test case data for reporting or debugging.

2. State Management:
    - Stores the state (NodeState) of the test case, ensuring consistency across workflow operations.

3. Integration with Workflow:
    - Acts as the bridge between the workflow (TCNode) and the higher-level application (e.g., user interfaces, data storage).

4. Isolation of Business Logic:
    - Separates the workflow-specific logic (in TCNode) from the data-specific operations (in TestCaseDataModel).
    
Current Usage in TCNode

1. State Management:
    - The state property in TCNode delegates directly TestCaseDataModel. This ensures that the state is stored consistently, while
    TCNode operates on a higher abstraction level.

2. Execution Tracking:
    - add_execution() is called on the TestCaseDataModel during execution, implying that the model stores execution history or 
    statistics.

3. Parent Relationship:
    - The parent_test_run attribute links the TestCaseDataModel to its TestRun. While useful for certain operations (like quarantining), 
    This introduces a bidirectional reference that you've already decided to remove in favor of event-driven communication.


Potential Improvements
1. Remove Bidirectional Relationship
    - The parent_test_run attribute creates unnecessary coupling between TestCaseDataModel and TestRun. Instead, rely on events (SystemEventBus)
    for interactions with TestRun.
    
2. Explicit Responsibility Separation
    - Ensure TestCaseDataModel focuses only on data storage and retrieval, leaving workflow-specific logic (like state transitions) to TCNode.

3. Enhance Execution Tracking
    - If TestCaseDataModel tracks execution history, ensure it's structured and easily queryable. For example, store a list of execution attempts
    with timestamps and results.

4. Expose Test Case Results:
    - Add properties or methods to extract aggregated test results or statistics for reporting purposes.
"""
