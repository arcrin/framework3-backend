from _Node._TestRunTerminalNode import TestRunTerminalNode
from _Application._SystemEventBus import SystemEventBus
from _Application._SystemEvent import NewTestCaseEvent
from typing import List, TYPE_CHECKING, Dict, cast
from uuid import uuid4
import logging

if TYPE_CHECKING:
    from _Application._DomainEntity._Panel import Panel
    from _Node._TCNode import TCNode


class TestRun:
    def __init__(
        self,
        test_profile,  # type: ignore
    ):
        self._id: str = uuid4().hex
        self._tc_nodes: List["TCNode"] = []
        self._failed_tasks: Dict[str, "TCNode"] = {}
        self._parent_panel: "Panel" = cast("Panel", None)
        # TODO: profile is downloaded once and stored somewhere, either Panel or Session
        self._test_profile = test_profile  # type: ignore
        self._logger = logging.getLogger("TestRun")
        self._test_run_terminal_node = TestRunTerminalNode(self)

    @property
    def id(self) -> str:
        return self._id

    @property
    def parent_panel_id(self) -> int:
        return self._parent_panel.id

    @property
    def parent_control_session_id(self) -> str:
        return self._parent_panel.parent_control_session.id

    @property
    def parent_panel(self) -> "Panel":
        return self._parent_panel
    
    @property
    def tc_nodes(self) -> List["TCNode"]:
        return self._tc_nodes

    @parent_panel.setter
    def parent_panel(self, value: "Panel"):
        if not self._parent_panel:
            self._parent_panel = value
        else:
            raise Exception("A test run can only have one parent panel")

    def add_to_failed_test_cases(self, tc_node: "TCNode"):
        self._failed_tasks[tc_node.id] = tc_node
        self._tc_nodes.remove(tc_node)

    async def retest_failed_test_cases(self, tc_id: str):
        tc_node = self._failed_tasks[tc_id]
        tc_node.mark_as_not_processed()
        await self.add_tc_node(tc_node)
        self._failed_tasks.pop(tc_id)

    async def add_tc_node(self, tc_node: "TCNode"):  # TODO: add test case event
        self._test_run_terminal_node.add_dependency(tc_node)
        self._tc_nodes.append(tc_node)
        tc_node.data_model.parent_test_run = self
        new_test_case_event = NewTestCaseEvent(tc_node)
        await SystemEventBus.publish(new_test_case_event)
        await tc_node.check_dependency_and_schedule_self()

    async def load_test_case(self):
        # TODO: request for user to scan serial number through an event. OR, create a SerialNmberRequest node?
        # TestRun is a domain entity. If a TestCase (also an entity) is wrapped inside a node then processes, 
        # a TestRun should be treated the same way.
        profile = self._test_profile()  # type: ignore
        for tc_node in profile.test_case_list:  # type: ignore
            await self.add_tc_node(tc_node)  # type: ignore

"""
Key Responsibilities of TestRun
1. Test Case Management:
    - Maintains a list of active test case nodes (_tc_nodes) and failed test cases (_failed_tasks), providing methods to add, retry, 
    or reinitialize test cases.
    - Encapsulates logic for adding test case nodes, including dependency management via the TestRunTerminalNode.

2. Integration with Workflow:
    - Uses TestRunTerminalNode to establish dependencies between test cases, ensuring proper execution order and termination conditions.
    - Triggers events (e.g., NewTestCaseEvent) via the SystemEventBus to notify other components about test case additions.

3. Panel and Profile Association:
    - The TestRun is associated with a parent Panel and uses a test_profile to load and configure test cases. The relationship with the 
    panel is currently managed via parent_panel.

4. Retesting and Dependency Re-scheduling:
    - Provides mechanisms to mark failed test cases for retesting, ensuring they are properly re-added to the workflow.

    
Suggestions for Improvement
1. Remove parent_panel Reference:
    - As per your goal of maintaining a strictly hierarchical structure, the parent_panel attribute and its related parent_panel_id and 
    parent_control_session_id properties should be removed. Communication and data flow from the TestRun to higher levels (like Panel or 
    Session) can be handled using the SystemEventBus.

2. Encapsulation of Test Profile Logic:
    - Currently, the test_profile logic is partly within TestRun (load_test_case) and partly expected to be outside (_test_profile() method).
    Centralizing profile handling could improve clarity and make it easier to test and modify.

        Example:
            Create a TestProfileManager class or service to encapsulate test profile loading and storage.

3. Lifecycle Management:
    - Add lifecycle methods (e.g., start, stop, reset) to better define how a TestRun transitions through its phases. These methods could
    encapsulate initialization, cleanup, and reconfiguration logic.

4. Improved Error Handling for add_tc_node:
    - Adding a test case node involves multiple steps (dependency management, event publication, scheduling). Consider wrapping the entire 
    operation in a try-except block to ensure any failure doesn't leave the TestRun in an inconsistent state.

5. Batch Loading for load_test_case:
    - If loading test cases involves a large number of nodes, consider implementing batch addition or throttling to avoid overwhelming the 
    workflow or system resources.
    
"""