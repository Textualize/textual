from rich import print
from rich.panel import Panel

from textual.demo.demo_app import DemoApp

if __name__ == "__main__":
    app = DemoApp()
    app.run()
    print(
        Panel.fit(
            "[b magenta]Hope you liked the demo![/]\n\n"
            "Please consider sponsoring me if you get value from my work.\n\n"
            "Even the price of a ☕ can brighten my day!\n\n"
            "https://github.com/sponsors/willmcgugan\n\n"
            "- Will McGugan",
            border_style="red",
            title="Consider sponsoring",
        )
    )
