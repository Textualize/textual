from textual.constants import _get_environ_bool, _get_environ_int, _get_environ_port


def test_environ_int(monkeypatch):
    """Check minimum is applied."""
    monkeypatch.setenv("FOO", "-1")
    assert _get_environ_int("FOO", 1, minimum=0) == 0
    monkeypatch.setenv("FOO", "0")
    assert _get_environ_int("FOO", 1, minimum=0) == 0
    monkeypatch.setenv("FOO", "1")
    assert _get_environ_int("FOO", 1, minimum=0) == 1


def test_environ_bool(monkeypatch):
    """Anything other than "1" is False."""
    monkeypatch.setenv("BOOL", "1")
    assert _get_environ_bool("BOOL") is True
    monkeypatch.setenv("BOOL", "")
    assert _get_environ_bool("BOOL") is False
    monkeypatch.setenv("BOOL", "0")
    assert _get_environ_bool("BOOL") is False


def test_environ_port(monkeypatch):
    """Valid ports are between 0 and 65536."""
    monkeypatch.setenv("PORT", "-1")
    assert _get_environ_port("PORT", 80) == 80
    monkeypatch.setenv("PORT", "0")
    assert _get_environ_port("PORT", 80) == 0
    monkeypatch.setenv("PORT", "65536")
    assert _get_environ_port("PORT", 80) == 80
