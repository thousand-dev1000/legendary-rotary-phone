#!/usr/bin/env python3
"""
WebSocket chat server — rotary-phone style room-based broadcasting.

Each WebSocket path is treated as a room name.  Every message sent by one
client is broadcast to all other clients in the same room.

Usage:
    python phone/ws_chat_server.py [host] [port]
"""

import asyncio
import logging
import sys
from collections import defaultdict

import websockets

logger = logging.getLogger(__name__)

# room name -> set of connected WebSocket clients
rooms: dict[str, set] = defaultdict(set)


async def handler(websocket, path: str = "/") -> None:
    room = path.strip("/") or "default"
    rooms[room].add(websocket)
    logger.info("Client joined room %r  (room size: %d)", room, len(rooms[room]))
    try:
        async for message in websocket:
            logger.debug("Room %r broadcast: %r", room, message)
            recipients = rooms[room] - {websocket}
            if recipients:
                await asyncio.gather(*(c.send(message) for c in recipients))
    except websockets.ConnectionClosedError:
        pass
    finally:
        rooms[room].discard(websocket)
        if not rooms[room]:
            del rooms[room]
        logger.info("Client left room %r", room)


async def main(host: str = "localhost", port: int = 8765) -> None:
    logging.basicConfig(level=logging.INFO)
    async with websockets.serve(handler, host, port):
        print(f"WebSocket chat server listening on ws://{host}:{port}/")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
    asyncio.run(main(host, port))
