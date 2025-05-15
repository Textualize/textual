import pytest

@pytest.fixture
def anyio_backend() -> object:
    return ("asyncio", {"debug": True})
