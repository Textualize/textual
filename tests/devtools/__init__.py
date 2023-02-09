import os
import sys

import pytest

_MACOS_CI = sys.platform == "darwin" and os.getenv("CI", "0") != "0"
_WINDOWS = sys.platform == "win32"

# TODO - this needs to be revisited - perhaps when aiohttp 4.0 is released?
# We get occasional test failures relating to devtools. These *appear* to be limited to MacOS,
# and the error messages suggest the event loop is being shutdown before async fixture
# teardown code has finished running. These are very rare, but are much more of an issue on
# CI since they can delay builds that have passed locally.
pytestmark = pytest.mark.skipif(_MACOS_CI or _WINDOWS, reason="Issue #411")
