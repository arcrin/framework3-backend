#type: ignore
from trio_websocket import serve_websocket, ConnectionClosed
import json
import logging
import trio


log_connections = set()

class WebSocketLogHandler(logging.Handler):
    def __init__(self, connections):
        super().__init__()
        self.connections = connections
        self.send_channel, self.receive_channel = trio.open_memory_channel(50)

    async def handle_log_message(self):
        async with self.send_channel:
            async for record in self.receive_channel:
                log_entry = self.format(record)
                message = json.dumps({'log': log_entry})   
                for connection in list(self.connections):
                    try:
                        await connection.send_message(message)
                    except ConnectionClosed:
                        print(f"Connection with {connection} lost")
                        self.connections.remove(connection)

        

    def emit(self, record) -> None:
        self.send_channel.send_nowait(record)


async def ws_log_handler(request):
    global log_connections
    ws = await request.accept()
    print(f"Connection with {ws} established")
    log_connections.add(ws)
    try:
        while True:
            await ws.get_message()
    except ConnectionClosed:
        print(f"Connection with {ws} lost")
    finally:
        log_connections.remove(ws)

async def run_log_server():
    await serve_websocket(ws_log_handler, 'localhost', 8000, ssl_context=None)

