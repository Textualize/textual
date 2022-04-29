from textual.app import App


def test_env_vaer(monkeypatch):
    monkeypatch.setenv("TEXTUAL", "")
    app = App()
    assert app.features == set()
    assert app.devtools_enabled is False

    monkeypatch.setenv("TEXTUAL", "devtools")
    app = App()
    assert app.features == {"devtools"}
    assert app.devtools_enabled is True


def test_devtools_enabled_property():

    app = App(_features="")
    assert app.devtools_enabled is False

    app = App(_features="devtools")
    assert app.devtools_enabled is True
