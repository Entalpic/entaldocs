# 𝚫 Siesta

**Siesta Is Entalpic'S Terminal Assistant.**

It is designed to help you with good practices in Python development at Entalpic, especially with boilerplate setup for projects and documentation.

## TL;DR

Use `siesta` to initialize

1. Start a new Python project from scratch

    ```bash
    siesta project quickstart --local
    ```

2. Add documentation to an existing project

    ```bash
    siesta docs init --local
    ```

3. Build the docs locally

    ```bash
    siesta docs build
    ```

4. Watch for changes and auto-rebuild the docs

    ```bash
    siesta docs watch
    ```

> [!NOTE]
> You can always get help with `siesta --help` or `siesta docs --help` or `siesta project --help`

## Installation

```bash
uv tool install git+ssh://git@github.com/entalpic/siesta.git
```

## Upgrade

```bash
uv tool upgrade siesta
```

See [**Usage instructions in the online docs**](https://entalpic-siesta.readthedocs-hosted.com/en/latest/autoapi/siesta/cli/index.html).

## Contributing

Using `uv`:

1. Clone this repository

    ```bash
    git clone git+ssh://git@github.com/entalpic/siesta.git
    # or
    gh repo clone entalpic/siesta

    # then
    cd siesta
    ```

2. `$ uv sync`
3. Build docs locally with `siesta docs build`
4. Open `docs/build/html/index.html`

That's it 🤓

## Status 🏗️

This is still very WIP. In particular, next steps:

-   Update Contribution Guide
-   Add ReadTheDocs deployment instructions
-   More tests
