from __future__ import annotations

import shlex
import sys
import subprocess
import threading
from pathlib import Path

target_script_name = "basic"
script_time_to_live = 2.0  # in seconds

if len(sys.argv) > 1:
    target_script_name = sys.argv[1]
if len(sys.argv) > 2:
    script_time_to_live = float(sys.argv[2])

e2e_root = Path(__file__).parent

completed_process = None


def launch_sandbox_script(python_file_name: str) -> None:
    global completed_process

    command = f"{sys.executable} ./test_apps/{shlex.quote(python_file_name)}.py"
    print(f"Launching command '{command}'...")
    try:
        completed_process = subprocess.run(
            command, shell=True, check=True, capture_output=True, cwd=str(e2e_root)
        )
    except subprocess.CalledProcessError as err:
        print(f"Process error: {err.stderr}")
        raise


thread = threading.Thread(
    target=launch_sandbox_script, args=(target_script_name,), daemon=True
)
thread.start()

print(
    f"Launching Python script in a sub-thread; we'll wait for it for {script_time_to_live} seconds..."
)
thread.join(timeout=script_time_to_live)
print("The wait is over.")

process_still_running = completed_process is None
process_was_able_to_run_without_errors = process_still_running

if process_was_able_to_run_without_errors:
    print("Python script is still running :-)")
else:
    print("Python script is no longer running :-/")

sys.exit(0 if process_was_able_to_run_without_errors else 1)
