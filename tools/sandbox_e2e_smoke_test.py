from __future__ import annotations
import sys
import multiprocessing
from pathlib import Path

project_root = Path(__file__).parent.parent
for python_path in [str(project_root), str(project_root / "src")]:
    sys.path.append(python_path)


def launch_sandbox_script():
    from sandbox.basic import app as basic_app

    basic_app.run()


process = multiprocessing.Process(target=launch_sandbox_script, daemon=True)
process.start()

process.join(timeout=2)

process_still_running = process.exitcode is None
process_was_able_to_run_without_errors = process_still_running
if process_still_running:
    process.kill()

sys.exit(0 if process_was_able_to_run_without_errors else 1)
