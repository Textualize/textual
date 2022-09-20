import difflib
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from operator import attrgetter
from os import PathLike
from pathlib import Path
from typing import Union, List, Optional, Callable

import pytest
from _pytest.config import ExitCode
from _pytest.fixtures import FixtureRequest
from _pytest.main import Session
from _pytest.terminal import TerminalReporter
from jinja2 import Template
from rich.console import Console
from rich.panel import Panel
from syrupy import SnapshotAssertion

from textual._doc import take_svg_screenshot

snapshot_svg_key = pytest.StashKey[str]()
actual_svg_key = pytest.StashKey[str]()
snapshot_pass = pytest.StashKey[bool]()


@pytest.fixture
def snap_compare(
    snapshot: SnapshotAssertion, request: FixtureRequest
) -> Callable[[str], bool]:
    """
    This fixture returns a function which can be used to compare the output of a Textual
    app with the output of the same app in the past. This is snapshot testing, and it
    used to catch regressions in output.
    """

    def compare(app_path: str, snapshot: SnapshotAssertion) -> bool:
        node = request.node
        actual_screenshot = take_svg_screenshot(app_path)
        result = snapshot == actual_screenshot

        if result is False:
            # The split and join below is a mad hack, sorry...
            node.stash[snapshot_svg_key] = "\n".join(str(snapshot).splitlines()[1:-1])
            node.stash[actual_svg_key] = actual_screenshot
        else:
            node.stash[snapshot_pass] = True

        return result

    return partial(compare, snapshot=snapshot)


@dataclass
class SvgSnapshotDiff:
    snapshot: Optional[str]
    actual: Optional[str]
    test_name: str
    file_similarity: float
    path: PathLike
    line_number: int


def pytest_sessionfinish(
    session: Session,
    exitstatus: Union[int, ExitCode],
) -> None:
    """Called after whole test run finished, right before returning the exit status to the system.

    :param pytest.Session session: The pytest session object.
    :param int exitstatus: The status which pytest will return to the system.
    """
    diffs: List[SvgSnapshotDiff] = []
    num_snapshots_passing = 0
    for item in session.items:
        num_snapshots_passing += int(item.stash.get(snapshot_pass, False))
        snapshot_svg = item.stash.get(snapshot_svg_key, None)
        actual_svg = item.stash.get(actual_svg_key, None)
        if snapshot_svg and actual_svg:
            path, line_index, name = item.reportinfo()
            diffs.append(
                SvgSnapshotDiff(
                    snapshot=str(snapshot_svg),
                    actual=str(actual_svg),
                    file_similarity=100
                    * difflib.SequenceMatcher(
                        a=str(snapshot_svg), b=str(actual_svg)
                    ).ratio(),
                    test_name=name,
                    path=path,
                    line_number=line_index + 1,
                )
            )

    # TODO: Skipping writing artifacts on Windows on CI for now
    is_windows_ci = sys.platform == "win32" and os.getenv("CI") is not None
    if diffs and not is_windows_ci:
        diff_sort_key = attrgetter("file_similarity")
        diffs = list(reversed(sorted(diffs, key=diff_sort_key)))

        conftest_path = Path(__file__)
        snapshot_template_path = (
            conftest_path.parent / "snapshot_report_template.jinja2"
        )
        snapshot_report_path_dir = conftest_path.parent / "output"
        snapshot_report_path_dir.mkdir(parents=True, exist_ok=True)
        snapshot_report_path = snapshot_report_path_dir / "snapshot_report.html"

        template = Template(snapshot_template_path.read_text())

        num_fails = len(diffs)
        num_snapshot_tests = len(diffs) + num_snapshots_passing

        rendered_report = template.render(
            diffs=diffs,
            passes=num_snapshots_passing,
            fails=num_fails,
            pass_percentage=100 * (num_snapshots_passing / max(num_snapshot_tests, 1)),
            fail_percentage=100 * (num_fails / max(num_snapshot_tests, 1)),
            num_snapshot_tests=num_snapshot_tests,
            now=datetime.utcnow(),
        )
        with open(snapshot_report_path, "w+") as snapshot_file:
            snapshot_file.write(rendered_report)

        session.config._textual_snapshots = diffs
        session.config._textual_snapshot_html_report = snapshot_report_path


def pytest_terminal_summary(
    terminalreporter: TerminalReporter,
    exitstatus: ExitCode,
    config: pytest.Config,
) -> None:
    """Add a section to terminal summary reporting.

    :param _pytest.terminal.TerminalReporter terminalreporter: The internal terminal reporter object.
    :param int exitstatus: The exit status that will be reported back to the OS.
    :param pytest.Config config: The pytest config object.
    """
    diffs = getattr(config, "_textual_snapshots", None)
    console = Console()
    if diffs:
        snapshot_report_location = config._textual_snapshot_html_report
        summary_panel = Panel(
            f"[b]Report available for {len(diffs)} snapshot test failures.[/]\n\nView the report at:\n\n[blue]{snapshot_report_location}[/]",
            title="[b red]Textual Snapshot Test Summary",
            padding=1,
        )
        console.print(summary_panel)
