__all__ = ["cell_len"]

try:
    from rich.cells import cached_cell_len as cell_len
except ImportError:
    from rich.cells import cell_len
