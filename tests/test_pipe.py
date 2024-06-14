import subprocess
import sys
from pathlib import Path

import pytest

skip_windows = pytest.mark.skipif(
    sys.platform == "win32", reason="Syntax not supported on Windows"
)


@skip_windows
def test_deadlock():
    """Regression test for https://github.com/Textualize/textual/issues/4643"""
    app_path = (Path(__file__) / "../deadlock.py").resolve().absolute()
    result = subprocess.run(
        f'echo q | python "{app_path}"', shell=True, capture_output=True
    )
    print(result.stdout)
    assert result.returncode == 0
