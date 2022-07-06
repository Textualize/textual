import pytest

from textual._config import Config

TEST_APP_NAME = "not_hotdog"


@pytest.fixture
def packaged_default_config(tmp_path):
    """By 'packaged default config' we mean the configuration file that gets shipped alongside
    a Textual application, and which contains the default configuration values."""
    config = tmp_path / "textual.toml"
    config.write_text(
        f"""
    [meta]  # This section should be ignored since it's for user config only
    version = "1.0"

    [textual.devtools]  # Global config as part of defaults packaged with an app? Should be excluded.
    enabled = true
    this_key_cant_be_set_here = 1

    [{TEST_APP_NAME}]  # Namespaced config in the packaged defaults is fine though
    debug = false

    [{TEST_APP_NAME}.config]  # App "sandbox" for application-specific configuration
    custom_config = "hello"
    another_config = "world"

    [{TEST_APP_NAME}.devtools]
    a = 2
    c = 4

    [some_other_app]  # Your app can't impact config of another app
    x = 1
    """
    )
    return config


@pytest.fixture
def user_config(tmp_path):
    config = tmp_path / "user_config" / "textual.toml"
    config.parent.mkdir()
    config.write_text(
        f"""
    [meta]
    abc = 123

    [textual]
    debug = true
    dark = false

    [textual.devtools]
    enabled = false

    [{TEST_APP_NAME}]
    dark = true

    [{TEST_APP_NAME}.config]
    another_config = "override"

    [{TEST_APP_NAME}.devtools]
    a = 1
    b = 2

    [some_other_app]  # User config can, of course, contain other app config, but its not relevant to *this* app.
    y = 1
    """
    )
    return config


def test_resolve_reads_files_and_merges_sections_correctly(
    packaged_default_config, user_config
):
    """This is quite a large test but the whole configuration flow has many steps, so it's worth
    have a test of the intermediary state here.
    This tests the process of reading user config and the default config packaged with the app, and
    ensures that corresponding values are merged correctly, and that only properly namespaced values in
    the packaged default config is included."""
    config = Config(
        namespace=TEST_APP_NAME,
        default_config_path=packaged_default_config,
        user_config_paths=[user_config],
    )

    config.resolve()

    assert (
        config.raw
        == {  # [not_hotdog] sections from packaged/default config and user config merged
            "config": {
                "another_config": "override",  # Appears in both user config and packaged defaults, user-config wins.
                "custom_config": "hello",  # Appears only in packaged defaults, with no user overrides.
            },
            "dark": True,  # From the user's app config
            "debug": False,  # From the default app packaged config
            "devtools": {
                "a": 1,
                "b": 2,
                "c": 4,
                "enabled": False,
            },
        }
    )
    assert config["dark"] is True
    # [meta] section retrieved from user config, [meta] from packaged defaults ignored
    assert config.meta == {
        "abc": 123,
    }


def test_empty_user_config_but_not_empty_packaged_defaults(
    tmp_path, packaged_default_config
):
    user_config_path = tmp_path / "user-config-textual.toml"
    user_config_path.write_text("")

    config = Config(
        TEST_APP_NAME,
        default_config_path=packaged_default_config,
        user_config_paths=[user_config_path],
    )
    config.resolve()

    assert config.raw == {
        "config": {"another_config": "world", "custom_config": "hello"},
        "debug": False,
        "devtools": {"a": 2, "c": 4},
    }
    assert config.meta == {}


def test_empty_packaged_defaults_but_not_empty_user_config(tmp_path, user_config):
    packaged_default_config_path = tmp_path / "packaged-defaults-textual.toml"
    packaged_default_config_path.write_text("")

    config = Config(
        TEST_APP_NAME,
        default_config_path=packaged_default_config_path,
        user_config_paths=[user_config],
    )
    config.resolve()

    assert config.raw == {
        "config": {"another_config": "override"},
        "dark": True,
        "debug": True,
        "devtools": {"a": 1, "b": 2, "enabled": False},
    }
    assert config.meta == {"abc": 123}


def test_empty_config_files(tmp_path):
    packaged_default_config_path = tmp_path / "packaged-defaults-textual.toml"
    user_config_path = tmp_path / "packaged-defaults-textual.toml"

    packaged_default_config_path.write_text("")
    user_config_path.write_text("")

    config = Config(
        TEST_APP_NAME,
        default_config_path=packaged_default_config_path,
        user_config_paths=[user_config_path],
    )
    config.resolve()

    assert config.raw == {"config": {}, "devtools": {}}
    assert config.meta == {}


def test_packaged_default_config_file_doesnt_exist(tmp_path, user_config):
    non_existent_config_path = tmp_path / "i" / "dont" / "exist.toml"
    config = Config(
        TEST_APP_NAME,
        default_config_path=non_existent_config_path,
        user_config_paths=[user_config],
    )
    config.resolve()

    assert config.raw == {
        "config": {"another_config": "override"},
        "dark": True,
        "debug": True,
        "devtools": {"a": 1, "b": 2, "enabled": False},
    }
    assert config.meta == {"abc": 123}


def test_user_config_files_dont_exist(tmp_path, packaged_default_config):
    # This is a highly likely scenario. Config will receive the locations where configuration files
    # could exist. It's likely that they won't exist for the majority of users, however.
    non_existent_config_path = tmp_path / "i" / "dont" / "exist.toml"
    config = Config(
        TEST_APP_NAME,
        default_config_path=packaged_default_config,
        user_config_paths=[non_existent_config_path],
    )
    config.resolve()

    assert config.raw == {
        "config": {"another_config": "world", "custom_config": "hello"},
        "debug": False,
        "devtools": {"a": 2, "c": 4},
    }
    assert config.meta == {}


def test_no_config_files_exist_at_all(tmp_path):
    user_config_path = tmp_path / "i" / "dont" / "exist.toml"
    packaged_default_config_path = tmp_path / "i" / "also" / "dont" / "exist.toml"

    config = Config(
        TEST_APP_NAME,
        default_config_path=packaged_default_config_path,
        user_config_paths=[user_config_path],
    )

    config.resolve()

    assert config.raw == {'devtools': {}}
    assert config.meta == {}
