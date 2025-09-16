# 𝚫 Siesta

**Siesta Is Entalpic'S Terminal Assistant.**

It is designed to help you with good practices in Python development at Entalpic, especially with boilerplate setup for projects and documentation.

## CL

Use `siesta` to initialize a documentation infrastructure in your current codebase. Refer to the docs for usage[FIXME].

## Installation

```bash
uv tool install git+ssh://git@github.com/entalpic/siesta.git
```

## Upgrade

```bash
uv tool upgrade siesta
```

See Usage instructions [in the online docs](https://entalpic-siesta.readthedocs-hosted.com/en/latest/autoapi/siesta/cli/index.html).

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
