"""
Source code for the ``entaldocs`` Command-Line Interface (CLI).

Learn how to use with:

.. code-block:: bash

    $ entaldocs --help
    $ entaldocs init --help
    $ entaldocs show-deps --help

You can also refer to the :ref:`entaldocs-cli-tutorial` for more information.
"""

import sys
from shutil import rmtree
from subprocess import run

from cyclopts import App, Parameter
from rich import print

from entaldocs.utils import (
    copy_defaults_folder,
    install_dependencies,
    load_deps,
    logger,
    make_empty_folders,
    overwrite_docs_files,
    resolve_path,
)

app = App(
    help="A CLI tool to initialize a Sphinx documentation project with standard Entalpic config.",
    default_parameter=Parameter(negative=()),
)
""":py:class:`cyclopts.App`: The main CLI application."""


@app.command
def init(
    path: str = "./docs",
    as_main: bool = None,
    overwrite: bool = False,
    deps: bool = None,
    uv: bool = None,
    with_defaults: bool = False,
):
    """Initialize a Sphinx documentation project with Entalpic's standard configuration.

    In particular:

    - Initializes a new Sphinx project at the specified path.

    - Optionally installs recommended dependencies (run `entaldocs show-deps` to see them).

    - Uses the split source / build folder structure.

    - Includes standard `conf.py` and `index.rst` files with good defaults.

    .. warning::

        If you don't install the dependencies here, you will need to install them manually.

    .. important::

        Update the placeholders (``$FILL_HERE``) in the generated files with the appropriate values before you
        build the documentation.

    .. tip::

        Build the local HTML docs by running ``$ make clean && make html`` from the documentation folder.

    Parameters
    ----------
    path : str, optional
        Where to store the docs.
    as_main : bool, optional
        Whether docs dependencies should be included in the main or dev dependencies.
    overwrite : bool, optional
        Whether to overwrite existing docs (if any).
    deps : bool, optional
        Prevent dependencies prompt by forcing its value to ``True`` or ``False``.
    uv : bool, optional
        Prevent uv prompt by forcing its value to ``True`` or ``False``.
    with_defaults: bool, optional
        Whether to trust the defaults and skip all prompts.

    Raises
    ------
    sys.exit(1)
        If the path already exists and ``--overwrite`` is not provided.
    """
    # where the docs will be stored, typically `$CWD/docs`
    path = resolve_path(path)
    print(f"[blue]Initializing at path:[/blue] {path}")
    if path.exists():
        # docs folder already exists
        if not overwrite:
            # user doesn't want to overwrite -> abort
            print(f"Path already exists: {path}")
            print("Use --overwrite to overwrite.")
            logger.abort("Aborting.")
        # user wants to overwrite -> remove the folder and warn
        print("🚧 Overwriting path.")
        rmtree(path)

    # create the docs folder
    path.mkdir(parents=True)
    print("Initialized.")

    # setting defaults
    if with_defaults:
        if deps is not None:
            print("Ignoring deps argument because you are using --with-defaults.")
        deps = True
        if as_main is not None:
            print("Ignoring as_main argument because you are using --with-defaults.")
        as_main = False

    # whether to install dependencies
    should_install = deps is not None or logger.confirm(
        "Would you like to install recommended dependencies?"
    )
    if should_install:
        with_uv = False
        # check if uv.lock exists in order to decide whether to use uv or not
        if resolve_path("./uv.lock").exists():
            with_uv = (
                uv
                or with_defaults  # if using defaults, assume uv since uv.lock exists
                or logger.confirm(
                    "It looks like you are using uv. Use `uv add` to add dependencies?"
                )
            )
        else:
            if uv:
                print(
                    "uv.lock not found. Skipping uv dependencies, installing with pip."
                )
        print(f"Installing dependencies{' with uv.' if with_uv else '.'}..")
        # execute the command to install dependencies
        install_dependencies(with_uv, with_uv and not as_main)
        print("[green]Dependencies installed.[green]")
    else:
        print("Skipping dependency installation.")

    # copy entaldocs pre-filled folder structure to the target directory
    copy_defaults_folder(path)
    # make empty dirs (_build and _static) in target directory
    make_empty_folders(path)
    # update defaults from user config
    overwrite_docs_files(path, with_defaults)

    print(
        "[blue]Now go to your newly created docs folder and update placehodlers in"
        + " [r] conf.py [/r] with the appropriate values.[/blue]",
    )
    print("Building your docs with [r] cd docs && make html [/r]")
    run(["make", "html"], cwd=str(path), check=True)
    print(
        f"🚀 [blue]Docs built![/blue] Open {path / 'build/html/index.html'} to see them."
    )
    print("[green]Happy documenting![/green]")
    sys.exit(0)


@app.command
def show_deps(as_pip: bool = False):
    """Show the recommended dependencies for the documentation that would be installed with `entaldocs init`.

    Parameters
    ----------
    as_pip : bool, optional
        Show as pip install command.
    """
    deps = load_deps()
    if as_pip:
        print(" ".join(deps))
    else:
        print("Dependencies:")
        for dep_and_ver in deps:
            print("  • " + dep_and_ver)


@app.command
def update(path: str = "./docs"):
    """
    Update the static files in the docs folder like CSS, JS and images.
    """

    path = resolve_path(path)
    if not path.exists():
        logger.abort(f"Path not found: {path}")
    if not logger.confirm("This will overwrite the static files. Continue?"):
        logger.abort("Aborting.")
    static = path / "source" / "_static"
    if not static.exists():
        logger.abort(f"Static folder not found: {static}")
    copy_defaults_folder(path, overwrite=False)
    logger.success("Static files updated.")
