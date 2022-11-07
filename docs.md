# Documentation Workflow

* [Install Hatch](https://hatch.pypa.io/latest/install/)
* Run the live-reload server using `hatch run docs:serve` from the project root
* Create new pages by adding new directories and Markdown files inside `docs/*`

## Commands

- `hatch run docs:serve` - Start the live-reloading docs server.
- `hatch run docs:build` - Build the documentation site.
- `hatch run docs:help` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
