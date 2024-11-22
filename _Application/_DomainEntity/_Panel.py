from typing import TYPE_CHECKING, cast, List
from _Application._DomainEntity._TestRun import TestRun
import logging

if TYPE_CHECKING:
    from _Application._DomainEntity._Session import ControlSession
    from _Application._DomainEntity._TestRun import TestRun
    from _Node._TCNode import TCNode


class Panel:
    def __init__(
        self,
        panel_id: int,
        test_profile,  # type: ignore
    ):
        self._id = panel_id
        self._test_run: "TestRun | None" = None
        self._parent_control_session: "ControlSession" = cast("ControlSession", None)
        self._test_profile = test_profile  # type: ignore
        self._logger = logging.getLogger("Panel")
        # TODO: test jig hard ware related code should be in this class

    @property
    def id(self):
        return self._id

    @property
    def parent_control_session_id(self):
        return self._parent_control_session.id

    @property
    def parent_control_session(self):
        return self._parent_control_session

    @property
    def test_run(self):
        return self._test_run
    
    @property
    def tc_nodes(self) -> List["TCNode"]:
        if self._test_run:
            return self._test_run.tc_nodes
        else:
            raise ValueError(f"Not test run associated with panel {self.id}")

    @parent_control_session.setter
    def parent_control_session(self, value: "ControlSession"):
        self._parent_control_session = value

    async def add_test_run(self):
        if not self._test_run:
            self._test_run = TestRun(
                self._test_profile,  # type: ignore
            )
            self._logger.info(f"TestRun {self._test_run.id} added")
            self._test_run.parent_panel = self
        else:
            raise Exception("A panel can only have one test run")

    def remove_test_run(self):
        self._test_run = None
        self._logger.info("TestRun removed")

"""
Key Responsibilities of Panel
1. Representation:
    - The Panel class represents a physical Panel in the test jig, which is associated with a specific ControlSession.
    - Each Panel has a unique id and is initialized with a test_profile that likely defines testing parameters or configurations.
2. Test Run Management:
    - A Panel can have at most one active TestRun at a time.
    - add_test_run initializes a new TestRun and associates it with the panel.
    - remove_test_run clears the current TestRun, effectively resetting the panel for a new test
3. Parent Control Session:
    - The panel knows its parent control session, enabling it to interact with session-level configurations or restrictions.
4. Access to Test Case Nodes(tc_nodes):
    - The tc_nodes property provides access to the test case nodes (TCNode) from the associated TestRun. This enforces the dependency 
    between Panel and TestRun.

Suggestions for Improvements
1. Encapsulation of Hardware Interaction:
    - The TODO in the class suggests moving test jig hardware interaction logic into Panel. THis is a good idea since the panel is a 
    natural place to encapsulate hardware-related code specific to its physical configuration or state.
    - Examples of hardware-specific logic:
        - Activation/Deactivation: Code to power on or off the hardware associated with the panel.
        - Calibration: Methods to handle panel-specific calibration routines.
        - Status Checks: Functions to retrieve the panel's hardware status (e.g., ready/not ready).

2. Error Handling for tc_nodes Access:
    - If there's no associated TestRun, tc_nodes raises a ValueError. While this is logical, you could make it more user-friendly by 
    including a detailed error message.
    - Alternatively, return an empty list or None to signal the absence of test case nodes, depending on your application's needs.

3. Panel Lifecycle Management:
    - Panels may require additional lifecycle methods to manage their state. For example:
        - Resetting: A method to reset the panel's state and clear any associated data.
        - Error Recovery: Amethod to handle hardware or software failures and reinitialize the panel.

4. Future Integration with test jig Configuration:
    - Since the panel is tied to the test jig, consider adding methods or properties to retrieve or set panel-specific configurations, such as:
        - Position or slot on the jig.
        - Panel-specific test parameters.

5. Logging Enhancements:
    - Adding more detailed logging, especially in methods like add_test_run and remove_test_run, can help during debugging and monitoring.
    

Bidirectional Access (Panel -> Parent Session)
When does it make sense:
1. Panels Need Context:
    - If a Panel frequently needs information from its parent session (e.g., session ID, configuration, user details), having direct access to the 
    parent session can simplify the code and reduce dependencies on external systems or parameters.
    - For example, if hardware configuration for a Panel depends on details from the ControlSession, direct access to the session can make these 
    interactions more straightforward.
2. Session-Scoped Operations:
    - If a Panel needs occasionally perform session-level operations (e.g., notify session about status updates or configuration change), having
    a direct access to its parent control session can facilitate this communication.
3. Encapsulation:'
    - By encapsulating the relationship in the Panel, you avoid passing session references through multiple layers of code, which can lead to tighter 
    coupling and more brittle code.

When to Avoid Bidirectional Access
1. Unnecessary Coupling:
    - If the Panel doesn't rely on its parent session for operations, the reference to the parent session may introduce unnecessary coupling, 
    making it harder to test or reuse Panel independently.
    - For instance, if Panel primarily interacts with its TestRun or directly with hardware, access to the ControlSession may not be required.
2. Risk of Cyclic dependencies:
    - Bidirectional relationships can cometimes create cyclic dependencies, complicating object lifecycle management (e.g., in garbage collection 
    or dependency injection scenarios).
3. Responsibility Misalignment:
    - If session-level operations belong in the session itself (e.g., aggregating test results), allowing the Panel to access the session may 
    encourage mixing responsibilities, leading to less cohesive code.
    
Alternative to Bidirectional Access
1. Use Event-Based Communication:
    - Instead of having Panel directly interact with its parent session, you can use an event-driven model (e.g., SystemEventBus) to notify the session
    about panel-related updates. THis removes direct coupling while maintaining communication.
2. Explicit Context Passing
    - If only specific operations require session details, you could pass the session context as a parameter to those operations rather than storing 
    it in the Panel. (Is this dependency injection?)

        async def activate(self, session_context):
            # Use session_context for configuration
            pass

3. Parent Session Management:
    - Keep the Panel unaware of its parent session. Instead, the parent session could act as the intermediary, managing all interactions with its panels.

Decision in Your Context
In the automated testing system:
    - Panels are strongly tied to their parent session, as they are created and manged within the context of a ControlSession. The session likely 
    dictates test profiles, hardware configurations, and overall workflow, so having access to the parent session makes practical sense.
    - The relationship is not purely hierarchical but contextual; the session and panel work closely together to model the testing process.

Given this, it is reasonable to allow a Panel to have access to its parent session. However, ensure that the responsibilities remain clear:
    - The Panel should not directly manipulate the ControlSession. Instead, it should only query information or notify the session when needed.
    - Use proper abstraction to avoid creating excessive coupling or reliance.
"""