from click.testing import CliRunner

import textual
from textual.cli.cli import run


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(run, ["--version"])
    assert textual.__version__ in result.output, "You need to update __version__"
