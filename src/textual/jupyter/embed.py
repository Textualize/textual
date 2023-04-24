from string import Template
from uuid import uuid4

from ..app import App
from .server import Server

TERMINAL_HTML = Template(
    """
<div
    id="terminal-${widget_id}"
    class="textual-terminal"
    data-session-websocket-url="${session_websocket_url}"
    data-background="${background}"
    data-color="${color}"
    style="width:100%;height:42em;background-color:${background}"
></div>

<link rel="stylesheet" href="${static_url}css/xterm.css">
<script src="${static_url}js/xterm.js"></script>
<script src="${static_url}js/xterm-addon-fit.js"></script>
<script src="${static_url}js/xterm-addon-webgl.js"></script>
<script src="${static_url}js/textual-serve.js"></script>
<script>
    (function run(){

        setTimeout(()=>{
            const element = document.querySelector("#terminal-${widget_id}");
            var textual_terminal = new TextualTerminal(element);
            textual_terminal.fit();
            textual_terminal.connect();
        }, 1000);

    })();

</script>
"""
)


def generate_embed(app: App) -> str:
    server = Server(app)
    port = server.serve()

    static_url = f"http://localhost:{port}/"
    url = f"ws://localhost:{port}/terminal/ws/"

    widget_id = uuid4().hex

    html = TERMINAL_HTML.substitute(
        {
            "widget_id": widget_id,
            "static_url": static_url,
            "session_websocket_url": url,
            "background": "rgba(0,0,0,0.1)",
            "color": "white",
        }
    )
    return html
