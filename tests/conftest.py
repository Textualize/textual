import pytest

from textual.devtools import _make_devtools_aiohttp_app
from textual.devtools_client import DevtoolsClient


@pytest.fixture
async def server(aiohttp_server, unused_tcp_port):
    app = _make_devtools_aiohttp_app(
        size_change_poll_delay_secs=0.001,
    )
    server = await aiohttp_server(app, port=unused_tcp_port)
    yield server
    await server.close()


@pytest.fixture
async def devtools(aiohttp_client, server):
    client = await aiohttp_client(server)
    devtools = DevtoolsClient(host=client.host, port=client.port)
    await devtools.connect()
    yield devtools
    await devtools.disconnect()
    await client.close()
