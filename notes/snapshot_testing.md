# Snapshot Testing


## What is snapshot testing?

Some tests that run for Textual are snapshot tests.
When you first run a snapshot test, a screenshot of an app is taken and saved to disk.
Next time you run it, another screenshot is taken and compared with the original one.

If the screenshots don't match, it means something has changed.
It's up to you to tell the test system whether that change is expected or not.

This allows us to easily catch regressions in how Textual outputs to the terminal.

Snapshot tests run alongside normal unit tests.

## How do I write a snapshot test?

1. Inject the `snap_compare` fixture into your test.
2. Pass in the path to the file which contains the Textual app.

```python
def test_grid_layout_basic_overflow(snap_compare):
    assert snap_compare("docs/examples/guide/layout/grid_layout2.py")
```

`snap_compare` can take additional arguments such as `press`, which allows
you to simulate key presses etc.
See the signature of `snap_compare` for more info.

## A snapshot test failed, what do I do?

When a snapshot test fails, a report will be created on your machine, and you
can use this report to visually compare the output from your test with the historical output for that test.

This report will be visible at the bottom of the terminal after the `pytest` session completes,
or, if running in CI, it will be available as an artifact attached to the GitHub Actions summary.

If you're happy that the new output of the app is correct, you can run `pytest` with the
`--snapshot-update` flag. This flag will update the snapshots for any test that is executed in the run,
so to update a snapshot for a single test, run only that test.

With your snapshot on disk updated to match the new output, running the test again should result in a pass.
