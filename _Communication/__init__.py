"""
Core Responsibilities of the Communication Interface
1. Connection Management
    - Establishing and Closing Connections: Methods to open and close connections for different protocols 
    (e.g., WebSocket, HTTP, or other real-time protocols).
    - Connection Tracking: Maintaining a list of registry of active connections, especially if multiple clients (e.g., view sessions)
    connect simultaneously
    - Connection Reuse or Pooling: Efficiently reusing existing connections or establishing new ones as needed.

2. Message Handling
    - Sending Messages: A send method to transmit messages in the required format (e.g., JSON for WebSocket)
    - Receiving Messages: If the interface is bidirectional (e.g., WebSocket), it should also support receiving messages, allowing the 
    system to listen for incoming data or commands.
    - Broadcasting to Multiple Connections: Ability to send the same message to multiple connections at once (e.g., broadcasting logs
    or test results to all view sessions).

3. Protocol Abstraction
    - Unified Interface for Different Protocols: Allow different protocols to implement the same methods (e.g., send, receive, close).
    This way, each component using the interface doesn't need toworry about protocol-specific implementations.
    - Error Handling and Resilience: Define how errors(e.g., connection drops) are handled within each protocol. This might include 
    reconnection logic or error notifications.

4. Session and Role Management
    - Control vs. Sessions: Ability to distinguish between different types of sessions (e.g., control, view) and handle permissions 
    or role-specific behavior.
    - Session Lifecycle: Methods to initiate and terminate sessions, possibly providing hooks for session-specific behavior, like 
    configuring test jig access for control sessions.
    
5. Logging and Monitoring
    - Connection and Message Logging: Keep records of connections established, closed, or errors encountered.
    - Message Tracking: Optionally, log or track each message sent or received, useful for debugging or auditing.
    
    


This is similar to what I have now. Instead of using an interface, I have an implementation of the WS version. WSCommModule's dependency
on ASM doesn't make sense, I need to figure out a better way to do this. I believe the dependency comes from the need to access the 
connection registry. 

Merging the responsibilities of the MessageBroadcaster into the communication module could simplify the architecture by consolidating all
communication-related logic in one place. This would eliminate the need for an intermediate class, reducing complexity and potential 
duplication.

Potential Benefits of consolidation
1. Centralized Communication: 
    - All communication responsibilities, including sending, broadcasting, and session management, would reside in one module, making the 
    architecture cleaner and easier to understand.
2. Reduced coupling: 
    - Components like LogProcessor and UIRequestProcessor could interact directly with the communication module without relying on an 
    additional layer.
3. Streamlined Development:
    - Changes to communication protocols or the addition of new features (e.g., logging, broadcasting, etc.) would only require updates 
    in the communication module.

    
What Would Change?
- Broadcasting Responsibility:
    - Methods like broadcast_log and broadcast_test_case_results would move into the communication module, which already manages connections 
    and session types.
- Session-Aware Messaging
    - The communication module could differentiate between control and view sessions when broadcasting messages, eliminating the need for 
    separate handling in MEssageBroadcaster.

Things to Consider
1. Future Scalability
    - If responsibilities grow (e.g., adding multiple protocols or complex routing logic), reintroducing a separate broadcaster might make 
    sense to keep the communication module focused.
2. Error Handling and Resilience:
    - Ensuring robust error handling for connection drops, retries, or protocol-specific issues would now fall solely under the communication 
    module.
3. Testability:
    - Test coverage might need to be more comprehensive for the communication module since it would now handle both low-level connections 
    and higher-level message processing.
"""