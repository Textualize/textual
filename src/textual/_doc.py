import os


# This module defines our "Custom Fences", powered by SuperFences
# @link https://facelessuser.github.io/pymdown-extensions/extensions/superfences/#custom-fences
def format_svg(source, language, css_class, options, md, attrs, **kwargs):
    """A superfences formatter to insert a SVG screenshot."""

    os.environ["TEXTUAL"] = "headless"
    os.environ["TEXTUAL_SCREENSHOT"] = "0.2"
    os.environ["COLUMNS"] = attrs.get("columns", "80")
    os.environ["LINES"] = attrs.get("lines", "24")
    path = attrs.get("path")

    if path:
        cwd = os.getcwd()
        examples_path, filename = os.path.split(path)
        try:
            os.chdir(examples_path)
            with open(filename, "rt") as python_code:
                source = python_code.read()
            app_vars = {}
            exec(source, app_vars)

            app = app_vars["app"]
            app.run()
            svg = app._screenshot

        finally:
            os.chdir(cwd)
    else:
        app_vars = {}
        exec(source, app_vars)
        app = app_vars["app"]
        app.run()
        svg = app._screenshot
    return svg
