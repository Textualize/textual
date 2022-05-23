import os


def format_svg(source, language, css_class, options, md, attrs, **kwargs):
    os.environ["TEXTUAL"] = "headless"
    os.environ["TEXTUAL_SCREENSHOT"] = "0.1"
    os.environ["COLUMNS"] = attrs.get("columns", "80")
    os.environ["LINES"] = attrs.get("lines", "24")
    app_vars = {}
    exec(source, app_vars)
    app = app_vars["app"]
    app.run()
    svg = app._screenshot
    return svg
