import asyncio

import pytest
import websockets

from phone import ws_chat_server


@pytest.mark.asyncio
async def test_broadcast_between_two_clients():
    host = '127.0.0.1'
    port = 8766

    server = await websockets.serve(ws_chat_server.handler, host, port)
    # give the server a moment
    await asyncio.sleep(0.05)

    uri = f"ws://{host}:{port}/testroom"
    async with websockets.connect(uri) as ws1:
        async with websockets.connect(uri) as ws2:
            await ws1.send("hello-from-1")
            msg = await asyncio.wait_for(ws2.recv(), timeout=1.0)
            assert msg == "hello-from-1"

    server.close()
    await server.wait_closed()
