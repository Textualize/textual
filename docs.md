# Documentation Workflow

* Ensure you're inside a *Python 3.10+* virtual environment
* Run the live-reload server using `mkdocs serve` from the project root
* Create new pages by adding new directories and Markdown files inside `docs/*`

## Commands

- `mkdocs serve` - Start the live-reloading docs server.
- `mkdocs build` - Build the documentation site.
- `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
