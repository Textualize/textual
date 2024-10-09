from textual.containers import Vertical


class Page(Vertical):
    DEFAULT_CSS = """
    Page {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
    }
    """
