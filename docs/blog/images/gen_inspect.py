from rich import inspect
from rich.console import Console

c = Console(record=True, width=110)

f = open("foo.txt", "w")

inspect(f, console=c)
c.save_svg("inspect1.svg")


inspect(f, console=c, methods=True)
c.save_svg("inspect2.svg")


inspect(f, console=c, methods=True, help=True)
c.save_svg("inspect3.svg")
