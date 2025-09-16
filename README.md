# 𝚫 Entaldocs

Entalpic's Development Guidelines

## CL

Use `entaldocs` to initialize a documentation infrastructure in your current codebase. Refer to the docs for usage [WIP].

## Installation

```bash
uv tool install git+ssh://git@github.com/entalpic/entaldocs.git
```

## Upgrade

```bash
uv tool upgrade entaldocs
```

See Usage instructions [in the online docs](https://entalpic-entaldocs.readthedocs-hosted.com/en/latest/autoapi/entaldocs/cli/index.html).

## Contributing

Using `uv`:

1. Clone this repository

    ```bash
    git clone git+ssh://git@github.com/entalpic/entaldocs.git
    # or
    gh repo clone entalpic/entaldocs

    # then
    cd entaldocs
    ```

2. `$ uv sync`
3. Build docs locally with `entaldocs build-docs`
4. Open `docs/build/html/index.html`

That's it 🤓

## Status 🏗️

This is still very WIP. In particular, next steps:

-   Update Contribution Guide
-   Add ReadTheDocs deployment instructions
-   More tests
