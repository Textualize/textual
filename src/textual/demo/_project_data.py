from dataclasses import dataclass


@dataclass
class ProjectInfo:
    """Dataclass for storing project information."""

    title: str
    author: str
    url: str
    description: str
    repo_url_part: str


PROJECTS = [
    ProjectInfo(
        "Posting",
        "Darren Burns",
        "https://posting.sh/",
        "Posting is an HTTP client, not unlike Postman and Insomnia. As a TUI application, it can be used over SSH and enables efficient keyboard-centric workflows. ",
        "darrenburns/posting",
    ),
    ProjectInfo(
        "Memray",
        "Bloomberg",
        "https://github.com/bloomberg/memray",
        "Memray is a memory profiler for Python. It can track memory allocations in Python code, in native extension modules, and in the Python interpreter itself.",
        "bloomberg/memray",
    ),
    ProjectInfo(
        "Toolong",
        "Will McGugan",
        "https://github.com/Textualize/toolong",
        "A terminal application to view, tail, merge, and search log files (plus JSONL).",
        "Textualize/toolong",
    ),
    ProjectInfo(
        "Dolphie",
        "Charles Thompson",
        "https://github.com/charles-001/dolphie",
        "Your single pane of glass for real-time analytics into MySQL/MariaDB & ProxySQL",
        "charles-001/dolphie",
    ),
    ProjectInfo(
        "Harlequin",
        "Ted Conbeer",
        "https://harlequin.sh/",
        "Portable, powerful, colorful. An easy, fast, and beautiful database client for the terminal.",
        "tconbeer/harlequin",
    ),
    ProjectInfo(
        "Elia",
        "Darren Burns",
        "https://github.com/darrenburns/elia",
        "A snappy, keyboard-centric terminal user interface for interacting with large language models.",
        "darrenburns/elia",
    ),
    ProjectInfo(
        "Trogon",
        "Textualize",
        "https://github.com/Textualize/trogon",
        "Auto-generate friendly terminal user interfaces for command line apps.",
        "Textualize/trogon",
    ),
    ProjectInfo(
        "TFTUI - The Terraform textual UI",
        "Ido Avraham",
        "https://github.com/idoavrah/terraform-tui",
        "TFTUI is a powerful textual UI that empowers users to effortlessly view and interact with their Terraform state.",
        "idoavrah/terraform-tui",
    ),
    ProjectInfo(
        "RecoverPy",
        "Pablo Lecolinet",
        "https://github.com/PabloLec/RecoverPy",
        "RecoverPy is a powerful tool that leverages your system capabilities to recover lost files.",
        "PabloLec/RecoverPy",
    ),
    ProjectInfo(
        "Frogmouth",
        "Dave Pearson",
        "https://github.com/Textualize/frogmouth",
        "Frogmouth is a Markdown viewer / browser for your terminal, built with Textual.",
        "Textualize/frogmouth",
    ),
    ProjectInfo(
        "oterm",
        "Yiorgis Gozadinos",
        "https://github.com/ggozad/oterm",
        "The text-based terminal client for Ollama.",
        "ggozad/oterm",
    ),
    ProjectInfo(
        "logmerger",
        "Paul McGuire",
        "https://github.com/ptmcg/logmerger",
        "logmerger is a TUI for viewing a merged display of multiple log files, merged by timestamp.",
        "ptmcg/logmerger",
    ),
    ProjectInfo(
        "doit",
        "Murli Tawari",
        "https://github.com/dooit-org/dooit",
        "A todo manager that you didn't ask for, but needed!",
        "dooit-org/dooit",
    ),
]
