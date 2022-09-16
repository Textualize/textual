import difflib
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from operator import attrgetter
from os import PathLike
from pathlib import Path
from typing import Union, List, Optional, Any, Callable

import pytest
from _pytest.fixtures import FixtureDef, SubRequest, FixtureRequest
from jinja2 import Template
from rich.console import Console
from rich.panel import Panel

from textual._doc import take_svg_screenshot

snapshot_svg_key = pytest.StashKey[str]()
actual_svg_key = pytest.StashKey[str]()
snapshot_pass = pytest.StashKey[bool]()


@pytest.fixture
def snap_compare(snapshot, request: FixtureRequest) -> Callable[[str], bool]:
    def compare(app_path: str, snapshot) -> bool:
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


#
# def pytest_runtestloop(session: "Session") -> Optional[object]:

@pytest.hookimpl(hookwrapper=True)
def pytest_pyfunc_call(pyfuncitem: "pytest.Function") -> Optional[object]:
    """Call underlying test function.

    Stops at first non-None result, see :ref:`firstresult`.
    """
    # Before
    yield
    # After


def pytest_runtest_teardown(item: pytest.Item, nextitem: Optional[pytest.Item]) -> None:
    """Called to perform the teardown phase for a test item.

    The default implementation runs the finalizers and calls ``teardown()``
    on ``item`` and all of its parents (which need to be torn down). This
    includes running the teardown phase of fixtures required by the item (if
    they go out of scope).

    :param nextitem:
        The scheduled-to-be-next test item (None if no further test item is
        scheduled). This argument is used to perform exact teardowns, i.e.
        calling just enough finalizers so that nextitem only needs to call
        setup functions.
    """


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(
    fixturedef: FixtureDef[Any], request: SubRequest
) -> Optional[object]:
    """Perform fixture setup execution.

    :returns: The return value of the call to the fixture function.

    Stops at first non-None result, see :ref:`firstresult`.

    .. note::
        If the fixture function returns None, other implementations of
        this hook function will continue to be called, according to the
        behavior of the :ref:`firstresult` option.
    """
    value = yield
    value = value.get_result()
    value = repr(value)


def pytest_sessionfinish(
    session: "pytest.Session",
    exitstatus: Union[int, "pytest.ExitCode"],
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
                    file_similarity=100 * difflib.SequenceMatcher(a=str(snapshot_svg), b=str(actual_svg)).ratio(),
                    test_name=name,
                    path=path,
                    line_number=line_index + 1,
                )
            )

    diff_sort_key = attrgetter("file_similarity")
    diffs = sorted(diffs, key=diff_sort_key)

    conftest_path = Path(__file__)
    snapshot_template_path = conftest_path.parent / "snapshot_report_template.jinja2"
    snapshot_report_path = conftest_path.parent / "snapshot_report.html"

    template = Template(snapshot_template_path.read_text())

    num_fails = len(diffs)
    num_snapshot_tests = len(diffs) + num_snapshots_passing

    rendered_report = template.render(
        diffs=diffs,
        passes=num_snapshots_passing,
        fails=num_fails,
        pass_percentage=100*(num_snapshots_passing/num_snapshot_tests),
        fail_percentage=100*(num_fails/num_snapshot_tests),
        num_snapshot_tests=num_snapshot_tests,
        now=datetime.utcnow()
    )
    with open(snapshot_report_path, "wt") as snapshot_file:
        snapshot_file.write(rendered_report)

    session.config._textual_snapshots = diffs
    session.config._textual_snapshot_html_report = snapshot_report_path


def pytest_terminal_summary(
    terminalreporter: "pytest.TerminalReporter",
    exitstatus: pytest.ExitCode,
    config: pytest.Config,
) -> None:
    """Add a section to terminal summary reporting.

    :param _pytest.terminal.TerminalReporter terminalreporter: The internal terminal reporter object.
    :param int exitstatus: The exit status that will be reported back to the OS.
    :param pytest.Config config: The pytest config object.

    .. versionadded:: 4.2
        The ``config`` parameter.
    """
    diffs = config._textual_snapshots
    snapshot_report_location = config._textual_snapshot_html_report
    console = Console()
    summary_panel = Panel(
        f"[b]Report available for {len(diffs)} snapshot test failures.[/]\n\nView the report at:\n\n[blue]{snapshot_report_location}[/]",
        title="[b red]Textual Snapshot Test Summary", padding=1)
    console.print(summary_panel)
