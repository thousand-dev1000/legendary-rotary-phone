#!/usr/bin/env python3
"""Simple WebSocket chat server with room support (room == path).

Clients connect to ws://host:port/<room> and messages are broadcast to other
clients in the same room.
"""
import asyncio
from typing import Dict, Set

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
except Exception:
    websockets = None

ROOMS: Dict[str, Set[WebSocketServerProtocol]] = {}


async def handler(websocket: WebSocketServerProtocol, path: str):
    room = path.strip('/') or 'lobby'
    clients = ROOMS.setdefault(room, set())
    clients.add(websocket)
    print(f"Client joined room '{room}' (total: {len(clients)})")
    try:
        async for message in websocket:
            # Broadcast to other clients in room
            for peer in set(clients):
                if peer is websocket:
                    continue
                try:
                    await peer.send(message)
                except Exception:
                    pass
    finally:
        clients.remove(websocket)
        print(f"Client left room '{room}' (remaining: {len(clients)})")
        if not clients:
            ROOMS.pop(room, None)


async def run_server(host: str = '0.0.0.0', port: int = 8765):
    if websockets is None:
        print('websockets library not available. Install from requirements.txt')
        return

    print(f"Starting WebSocket chat server on {host}:{port}")
    async with websockets.serve(handler, host, port):
        print("Server running. Press Ctrl+C to stop.")
        await asyncio.Future()


if __name__ == '__main__':
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print('\nServer stopped.')
