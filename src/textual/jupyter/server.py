from __future__ import annotations

import asyncio
import json
import socket
from json import JSONDecodeError
from pathlib import Path
from threading import Thread

import aiohttp
from aiohttp import web

from ..app import App
from .driver import JupyterDriver


class Server:
    def __init__(self, app: App) -> None:
        self.app = app

    @classmethod
    def encode_packet(cls, packet_type: bytes, payload: bytes) -> bytes:
        packet_bytes = b"%s%s%s" % (
            packet_type,
            len(payload).to_bytes(4, "big"),
            payload,
        )
        return packet_bytes

    async def handle_terminal_websocket(self, request: web.Request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        driver = JupyterDriver(ws, self.app)

        app_task = asyncio.create_task(self.app.run_async(size=(80, 24), driver=driver))

        BINARY = aiohttp.WSMsgType.BINARY
        TEXT = aiohttp.WSMsgType.TEXT

        try:
            async for msg in ws:
                if msg.type == TEXT:
                    try:
                        packet = json.loads(msg.data)
                    except JSONDecodeError:
                        pass
                    else:
                        packet_type, payload = packet
                        if packet_type == "stdin":
                            driver.feed_stdin(payload)
                        else:
                            driver.on_meta(packet_type, payload)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print("ws connection closed with exception %s" % ws.exception())
        finally:
            if self.app._running:
                await self.app._shutdown()
            await app_task

        return ws

    def serve(self) -> int:
        server_socket = socket.socket()
        server_socket.bind(("", 0))
        port = server_socket.getsockname()[1]
        serve_thread = Thread(target=self._serve, args=(server_socket,))
        serve_thread.start()
        return port

    def _serve(self, server_socket: socket.socket) -> None:
        try:
            app = web.Application()
            router = app.router
            router.add_get(
                "/terminal/ws/",
                self.handle_terminal_websocket,
                name="session_websocket",
            )
            root_path = Path(__file__).parent
            router.add_routes(
                [
                    web.static("/", root_path / "static", name="static"),
                ],
            )

            web.run_app(app, port=0, sock=server_socket, handle_signals=False)
        finally:
            server_socket.close()
