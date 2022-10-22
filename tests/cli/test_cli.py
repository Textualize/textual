from click.testing import CliRunner
from importlib_metadata import version

from textual.cli.cli import run


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(run, ["--version"])
    assert version("textual") in result.output
