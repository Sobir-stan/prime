from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket
        print(f"User '{username}' connected via WebSocket.")

    def disconnect(self, username: str):
        if username in self.active_connections:
            del self.active_connections[username]
            print(f"User '{username}' disconnected.")

    async def send_personal_message(self, message: dict, username: str):
        if username in self.active_connections:
            websocket = self.active_connections[username]
            await websocket.send_json(message)
            print(f"Sent message to '{username}': {message}")

manager = ConnectionManager()
