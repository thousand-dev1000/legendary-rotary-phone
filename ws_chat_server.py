#!/usr/bin/env python3
"""Simple WebSocket chat server with room support (room == path).

Clients connect to ws://host:port/<room> and messages are broadcast to other
clients in the same room.

Improvements:
- Uses `logging` instead of prints
- Sanitizes room names
- Graceful shutdown on SIGINT/SIGTERM
"""
import asyncio
import logging
import re
import signal
from typing import Dict, Set

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
except Exception:
    websockets = None

_ROOM_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")
ROOMS: Dict[str, Set[WebSocketServerProtocol]] = {}

logger = logging.getLogger(__name__)


def _sanitize_room(path: str) -> str:
    room = path.strip('/') or 'lobby'
    if _ROOM_RE.match(room):
        return room
    # fallback to safe room name
    safe = re.sub(r'[^A-Za-z0-9_\-]', '_', room)[:64]
    logger.debug("Sanitized room '%s' -> '%s'", room, safe)
    return safe


async def handler(websocket: WebSocketServerProtocol, path: str):
    room = _sanitize_room(path)
    clients = ROOMS.setdefault(room, set())
    clients.add(websocket)
    logger.info("Client joined room '%s' (total: %d)", room, len(clients))
    try:
        async for message in websocket:
            # Broadcast to other clients in room
            for peer in set(clients):
                if peer is websocket:
                    continue
                try:
                    await peer.send(message)
                except (ConnectionClosedOK, ConnectionClosedError):
                    # will be cleaned up in finally
                    pass
                except Exception:
                    logger.exception("Error sending to peer in room %s", room)
    except Exception:
        logger.exception("Handler error for room %s", room)
    finally:
        clients.discard(websocket)
        logger.info("Client left room '%s' (remaining: %d)", room, len(clients))
        if not clients:
            ROOMS.pop(room, None)


async def run_server(host: str = '0.0.0.0', port: int = 8765):
    if websockets is None:
        logger.error('websockets library not available. Install from requirements.txt')
        return

    logging.basicConfig(level=logging.INFO)
    logger.info("Starting WebSocket chat server on %s:%d", host, port)

    shutdown_event = asyncio.Event()

    def _ask_shutdown():
        logger.info("Shutdown requested")
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _ask_shutdown)
        except NotImplementedError:
            # Windows event loop may not support add_signal_handler
            pass

    server = await websockets.serve(handler, host, port)

    logger.info("Server running. Press Ctrl+C to stop.")
    await shutdown_event.wait()

    # Begin shutdown
    logger.info("Closing server...")
    server.close()
    await server.wait_closed()

    # Close any remaining client connections
    conns = [ws for clients in ROOMS.values() for ws in clients]
    for ws in conns:
        try:
            await ws.close()
        except Exception:
            logger.exception("Error closing websocket")

    logger.info("Server stopped.")


if __name__ == '__main__':
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info('\nServer stopped.')
