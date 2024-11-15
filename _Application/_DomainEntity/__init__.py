"""
Summary of Domain Entities' Role and Boundaries

1. Session: Acts as the bridge between the user and the application, determining access type (control view).
The single control session ensures there's one "master" of the testing process, while view sessions for monitoring
without interfering with control.

2. Panel: Represents a physical placeholder for the unit, with a future focus on configuring the test jig based 
on the panel's position. This aligns well with real-world constraints where configuration may vary by panel location.

3. Test Run: Provides a framework for managing the lifecycle of tests on each panel, enforcing rules such as one test 
run per panel at a time, which prevents overlapping test executions.

4. Test Case and Parameters: Allow users to interact with and view test at a detailed level. TestCaseDataModel provides
a user-friendly view, while TCNode models the workflow execution, maintaining a clean distinction between the user
interface and backend operations.

5. Test Jig: Will serve as the central hardware controller, requiring initial setup and configuration before each test
run. Given its central role in interfacing with the hardware, it will likely encapsulate configuration and operational 
details specific to the testing equipment.

Next Steps and Considerations
- Session Management: Since sessions can vary in nature (control vs. view), implementing clear session lifecycle 
management will be essential. This includes starting, ending, and transferring sessions if the control session is 
handed over to another user.
- Panel and Test Jig Configuration: The interaction between panels and the test jig may involve more complex mapping.
A configuration service or mapping layer could link each panel to its required jig configuration service or mapping
layer could link each panel to its required jig configuration based on position.
- Hardware Initialization and Shutdown: The Test Jig entity could define methods for hardware setup and teardown, 
ensuring that each test run begins with the correct configuration and that resources are properly released afterward.
"""