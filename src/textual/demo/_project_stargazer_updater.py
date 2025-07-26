import httpx
import re
from os import path
from rich.console import Console
console = Console()
error_console = Console(stderr=True, style="bold red")
def main() -> None:
    to_replace = ""
    template = '\n    ProjectInfo(\n        "<repo>",\n        "<creator>",\n        "<url>",\n        "<description>",\n        "<stars>"\n    ),'
    # dictionary of items to replace
    dictionary = {
        "repos": [
            "Posting",
            "Memray",
            "Toolong",
            "Dolphie",
            "Harlequin",
            "Elia",
            "Trogon",
            "TFTUI - The Terraform textual UI",
            "RecoverPy",
            "Frogmouth",
            "oterm",
            "logmerger",
            "doit",
        ],
        "creator": [
            "Darren Burns",
            "Bloomberg",
            "Will McGugan",
            "Charles Thompson",
            "Ted Conbeer",
            "Darren Burns",
            "Textualize",
            "Ido Avraham",
            "Pablo Lecolinet",
            "Dave Pearson",
            "Yiorgis Gozadinos",
            "Paul McGuire",
            "Murli Tawari",
        ],
        "url": [
            "https://posting.sh/",
            "https://github.com/bloomberg/memray",
            "https://github.com/Textualize/toolong",
            "https://github.com/charles-001/dolphie",
            "https://harlequin.sh/",
            "https://github.com/darrenburns/elia",
            "https://github.com/Textualize/trogon",
            "https://github.com/idoavrah/terraform-tui",
            "https://github.com/PabloLec/RecoverPy",
            "https://github.com/Textualize/frogmouth",
            "https://github.com/ggozad/oterm",
            "https://github.com/ptmcg/logmerger",
            "https://github.com/dooit-org/dooit"
        ],
        "description": [
            "Posting is an HTTP client, not unlike Postman and Insomnia. As a TUI application, it can be used over SSH and enables efficient keyboard-centric workflows. ",
            "Memray is a memory profiler for Python. It can track memory allocations in Python code, in native extension modules, and in the Python interpreter itself.",
            "A terminal application to view, tail, merge, and search log files (plus JSONL).",
            "Your single pane of glass for real-time analytics into MySQL/MariaDB & ProxySQL",
            "Portable, powerful, colorful. An easy, fast, and beautiful database client for the terminal.",
            "A snappy, keyboard-centric terminal user interface for interacting with large language models.",
            "Auto-generate friendly terminal user interfaces for command line apps.",
            "TFTUI is a powerful textual UI that empowers users to effortlessly view and interact with their Terraform state.",
            "RecoverPy is a powerful tool that leverages your system capabilities to recover lost files.",
            "Frogmouth is a Markdown viewer / browser for your terminal, built with Textual.",
            "The text-based terminal client for Ollama.",
            "logmerger is a TUI for viewing a merged display of multiple log files, merged by timestamp.",
            "A todo manager that you didn't ask for, but needed!",
        ],
        "repo_url_part": [
            "darrenburns/posting",
            "bloomberg/memray",
            "Textualize/toolong",
            "charles-001/dolphie",
            "tconbeer/harlequin",
            "darrenburns/elia",
            "Textualize/trogon",
            "idoavrah/terraform-tui",
            "PabloLec/RecoverPy",
            "Textualize/frogmouth",
            "ggozad/oterm",
            "ptmcg/logmerger",
            "dooit-org/dooit",
        ],
    }
    for index in range(len(dictionary["repo_url_part"])):
        # get each repo
        console.log(f"Checking {dictionary['repo_url_part'][index]}")
        response = httpx.get(
            f"https://api.github.com/repos/{dictionary['repo_url_part'][index]}"
        )
        if response.status_code == 200:
            # get stargazers
            stargazers = response.json()["stargazers_count"]
            if stargazers // 1000 != 0:
                # humanize them
                stargazers = f"{stargazers // 1000}.{(stargazers % 1000) // 100}k"
            # replace them
            to_replace += (
                template.replace("<repo>", dictionary["repos"][index])
                .replace("<creator>", dictionary["creator"][index])
                .replace("<url>", dictionary["url"][index])
                .replace("<description>", dictionary["description"][index])
                .replace("<stars>", str(stargazers))
            )
        elif response.status_code == 403:
            # gh api rate limited
            error_console.log("GitHub has received too many requests and started rate limiting.")
            exit(1)
        else:
            # any other reason
            print(f"GET https://api.github.com/repos/{dictionary['repo_url_part']} returned status code {response.status_code}")
    # replace
    console.log("Fixing projects.py")
    with open(path.join(path.dirname(__file__), "projects.py"), "r") as projects_script_file:
        projects_file = projects_script_file.read()
    # find a pattern to replace
    search_pattern = r"PROJECTS = \[([^\]]+)\]"
    search_match = re.search(search_pattern,projects_file)
    if search_match:
        projects_file = projects_file.replace(search_match.group(1), to_replace + "\n")
    with open(path.join(path.dirname(__file__), "projects.py"), "w") as projects_script_file:
        projects_script_file.write(projects_file)
    console.log("Done!")
if __name__ == "__main__":
    main()
