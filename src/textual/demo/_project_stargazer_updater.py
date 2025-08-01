import httpx
import os
import json
from rich.console import Console

# Not using the Absolute reference because
# I can't get python to run it.
from _project_data import PROJECTS

console = Console()
error_console = Console(stderr=True, style="bold red")


def main() -> None:
    STARS = {}

    for project in PROJECTS:
        # get each repo
        console.log(f"Checking {project.repo_url_part}")
        response = httpx.get(f"https://api.github.com/repos/{project.repo_url_part}")
        if response.status_code == 200:
            # get stargazers
            stargazers = response.json()["stargazers_count"]
            if stargazers // 1000 != 0:
                # humanize them
                stargazers = f"{stargazers / 1000:.1f}k"
            else:
                stargazers = str(stargazers)
            STARS[project.title] = stargazers
        elif response.status_code == 403:
            # gh api rate limited
            error_console.log(
                "GitHub has received too many requests and started rate limiting."
            )
            exit(1)
        else:
            # any other reason
            print(
                f"GET https://api.github.com/repos/{project.repo_url_part} returned status code {response.status_code}"
            )
    # replace
    with open(
        os.path.join(os.path.dirname(__file__), "_project_stars.py"), "w"
    ) as file:
        file.write("STARS = " + json.dumps(STARS, indent=4))
    console.log("Done!")


if __name__ == "__main__":
    main()
