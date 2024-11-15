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
    - Error Handling and Resilience: Define how erors(e.g., connection drops) are handled within each protocol. This might include 
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
"""