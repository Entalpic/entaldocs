# Copyright 2025 Entalpic
"""
Source code for the ``siesta`` Command-Line Interface (CLI).

Learn how to use with:

.. code-block:: bash

    $ siesta --help
    $ siesta docs --help
    $ siesta docs init --help
    $ siesta docs update --help
    $ siesta project --help
    $ siesta project quickstart --help
    $ siesta set-github-pat --help
    $ siesta show-deps --help

You can also refer to the :ref:`siesta-cli-tutorial` for more information.
"""

import getpass
import time
from importlib import metadata
from pathlib import Path
from shutil import rmtree
from subprocess import run
from textwrap import dedent
from typing import Optional

from cyclopts import App
from rich import print
from watchdog.observers import Observer

from siesta.utils.common import (
    load_deps,
    logger,
    resolve_path,
    run_command,
    write_or_update_pre_commit_file,
)
from siesta.utils.docs import (
    AutoBuildDocs,
    copy_boilerplate,
    has_python_files,
    install_dependencies,
    make_empty_folders,
    overwrite_docs_files,
    update_conf_py,
    write_rtd_config,
)
from siesta.utils.github import get_user_pat

app = App(
    help=dedent(
        f"""
    Siesta Is Entalpic'S Terminal Assistant ({metadata.version("siesta")})
    
    A set of CLI tools to help you with good practices in Python development at Entalpic.

    Upgrade with ``$ uv tool upgrade siesta``.

    See Usage instructions in the online docs: https://entalpic-siesta.readthedocs-hosted.com/en/latest/autoapi/siesta/.
    """.strip()
    ),
)
""":py:class:`cyclopts.App`: The main CLI application."""

docs_app = App(
    name="docs",
    help=dedent(
        """
        Initialize, build and watch a Sphinx documentation project with standard Entalpic config.

        Upgrade with ``$ uv tool upgrade siesta``.

        See Usage instructions in the online docs: https://entalpic-siesta.readthedocs-hosted.com/en/latest/autoapi/siesta.

        """.strip(),
    ),
)

project_app = App(
    name="project",
    help=dedent(
        """
        Initialize a Python project with standard Entalpic config.

        Upgrade with ``$ uv tool upgrade siesta``.

        See Usage instructions in the online docs: https://entalpic-siesta.readthedocs-hosted.com/en/latest/autoapi/siesta.

        """.strip(),
    ),
)

app.command(docs_app)
app.command(project_app)


def main():
    """Run the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        logger.abort("\nAborted.", exit=1)


@docs_app.command(name="init")
def init_docs(
    path: str = "./docs",
    as_main_deps: bool = None,
    overwrite: bool = False,
    deps: bool = None,
    uv: bool = None,
    with_defaults: bool = True,
    branch: str = "main",
    contents: str = "src/siesta/boilerplate",
    local: bool = False,
):
    """Initialize a Sphinx documentation project with Entalpic's standard configuration (also called within ``siesta project quickstart``).

    In particular:

    - Initializes a new Sphinx project at the specified path.

    - Optionally installs recommended dependencies (run `siesta show-deps` to see
      them).

    - Uses the split source / build folder structure.

    - Includes standard `conf.py` and `index.rst` files with good defaults.

    .. warning::

        If you don't install the dependencies here, you will need to install them
        manually.

    .. important::

        Update the placeholders (``$FILL_HERE``) in the generated files with the
        appropriate values before you build the documentation.

    .. tip::

        Build the local HTML docs by running ``$ siesta docs build`` or ``$ siesta docs watch``.

    Parameters
    ----------
    path : str, optional
        Where to store the docs.
    as_main_deps : bool, optional
        Whether docs dependencies should be included in the main or dev dependencies.
    overwrite : bool, optional
        Whether to overwrite existing docs (if any).
    deps : bool, optional
        Prevent dependencies prompt by forcing its value to ``True`` or ``False``.
    uv : bool, optional
        Prevent uv prompt by forcing its value to ``True`` or ``False``.
    with_defaults: bool, optional
        Whether to trust the defaults and skip all prompts.
    branch : str, optional
        The branch to fetch the static files from.
    contents : str, optional
        The path to the static files in the repository.
    local : bool, optional
        Use local boilerplate docs assets instead of fetching from the repository.
        May update to outdated contents so avoid using this option.

    Raises
    ------
    sys.exit(1)
        If the path already exists and ``--overwrite`` is not provided.
    """
    # Check for Python files before proceeding
    if not has_python_files():
        logger.abort(
            "No Python files found in project. Documentation requires Python files to document.",
            exit=1,
        )

    # where the docs will be stored, typically `$CWD/docs`
    pat = get_user_pat()
    if not pat and not local:
        logger.warning(
            "You need to set a GitHub Personal Access Token"
            + " to fetch the latest static files."
        )
        logger.warning("Run [r]$ siesta set-github-pat --help[/r] to learn how to.")
        logger.abort("Aborting.", exit=1)

    path = resolve_path(path)
    print(f"[blue]Initializing at path:[/blue] {path}")
    if path.exists():
        # docs folder already exists
        if not overwrite:
            # user doesn't want to overwrite -> abort
            print(f"Path already exists: {path}")
            print("Use --overwrite to overwrite.")
            logger.abort("Aborting.", exit=1)
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
        if as_main_deps is not None:
            print(
                "Ignoring as_main_deps argument because you are using --with-defaults."
            )
        as_main_deps = False

    # whether to install dependencies
    should_install = deps is not None or logger.confirm(
        "Would you like to install recommended dependencies?"
    )
    with_uv = False
    if should_install:
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
        install_dependencies(with_uv, with_uv and not as_main_deps)
        print("[green]Dependencies installed.[green]")
    else:
        print("Skipping dependency installation.")

    # download and copy siesta pre-filled folder structure to the target directory
    copy_boilerplate(
        path, branch=branch, content_path=contents, overwrite=True, local=local
    )
    # make empty dirs (_build and _static) in target directory
    make_empty_folders(path)
    # update defaults from user config
    overwrite_docs_files(path, with_defaults)

    has_rtd = Path(".readthedocs.yaml").exists()
    if not has_rtd:
        write_rtd_config()
        logger.success("ReadTheDocs config written.")
    else:
        logger.info("ReadTheDocs config already exists.")

    logger.info(
        "Now go to your newly created docs folder and update placehodlers in"
        + " [r] conf.py [/r] with the appropriate values.",
    )
    try:
        command = ["make", "html"]
        if with_uv:
            command = ["uv", "run"] + command
        logger.info(
            f"Building your docs with [r] cd docs && {' '.join(command)} [/r]..."
        )
        run(command, cwd=str(path), check=True)
        print(
            f"🚀 [blue]Docs built![/blue] Open {path / 'build/html/index.html'} to see them."
        )
        logger.success("[green]Happy documenting![/green]")
    except Exception as e:
        logger.warning("Failed to build the docs.")
        logger.warning(e)
        print()
        logger.info(
            "You can try to build the docs manually by running the above command."
        )


@app.command(name="show-deps")
def show_deps(as_pip: bool = False):
    """Show the recommended dependencies for the documentation that would be installed with `siesta docs init`.

    Parameters
    ----------
    as_pip : bool, optional
        Show as pip install command.
    """
    deps = load_deps()
    if as_pip:
        print(" ".join([d for k in deps for d in deps[k]]))
    else:
        print("Dependencies:")
        for scope in deps:
            print("  • " + scope + ": " + " ".join(deps[scope]))


@docs_app.command(name="update")
def update(
    path: str = "./docs",
    branch: str = "main",
    contents: str = "src/siesta/boilerplate",
    local: bool = False,
):
    """
    Update the static files in the docs folder like CSS, JS and images.

    Basically will download the remote repository's static files into a local temporary
    folder, then will copy them in your docs ``source/_static`` folder.

    .. important::

        ``$ siesta update`` requires a GitHub Personal Access Token (PAT) to fetch
        the latest version of the documentation's static files etc. from the repository.
        Run ``$ siesta set-github-pat`` to do so.

    .. note::

        Existing files will be backed up to ``{filename}.bak`` before new files are
        copied.

    Parameters
    ----------
    path : str, optional
        The path to your documentation folder.
    branch : str, optional
        The branch to fetch the static files from.
    contents : str, optional
        The path to the static files in the repository.
    local : bool, optional
        Use local boilerplate docs assets instead of fetching from the repository.
        May update to outdated contents so avoid using this option.
    """
    path = resolve_path(path)
    if not path.exists():
        logger.abort(f"Path not found: {path}", exit=1)
    if logger.confirm("Overwrite the documentation's HTML static files. Continue?"):
        static = path / "source" / "_static"
        if not static.exists():
            logger.abort(f"Static folder not found: {static}", exit=1)
        copy_boilerplate(
            dest=path,
            branch=branch,
            content_path=contents,
            overwrite=False,
            include_files_regex="_static",
            local=local,
        )
        logger.success("Static files updated.")
    if logger.confirm("Would you like to update the conf.py file?"):
        update_conf_py(path, branch=branch)
        logger.success("[r]conf.py[/r] updated.")
    if logger.confirm("Would you like to update the pre-commit hooks?"):
        write_or_update_pre_commit_file()
        has_uv = Path("uv.lock").exists()
        if has_uv:
            run_command(["uv", "add", "--dev", "pre-commit"])
            run_command(["uv", "run", "pre-commit", "install"])
        else:
            run_command(["pre-commit", "install"])
        logger.success("Pre-commit hooks updated.")
    logger.success("Done.")


@app.command(name="set-github-pat")
def set_github_pat(pat: Optional[str] = ""):
    """
    Store a GitHub Personal Access Token (PAT) in your keyring.

    A Github PAT is required to fetch the latest version of the documentation's static
    files etc. from the repository.

    `About GitHub PAT <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#about-personal-access-tokens>`_

    `Creating Github a PAT <https://github.com/settings/personal-access-tokens>`_


    1. Go to ``Settings > Developer settings > Personal access tokens (fine-grained) >
       Generate new token``.
    2. Name it ``siesta``.
    3. Set ``Entalpic`` as resource owner
    4. Expire it in 1 year.
    5. Only select the ``siesta`` repository
    6. Set *Repository Permissions* to *Contents: Read* and *Metadata: Read*.
    7. Click on *Generate token*.


    Parameters
    ----------
    pat : str, optional
        The GitHub Personal Access Token.
    """
    from keyring import set_password

    assert isinstance(pat, str), "PAT must be a string."

    logger.warning(
        "Run [r]$ siesta set-github-pat --help[/r]"
        + " if you're not sure how to generate a PAT."
    )
    if not pat:
        pat = getpass.getpass("Enter your GitHub PAT (hidden): ")
    logger.confirm(
        f"Are you sure you want to set the GitHub PAT to {pat[:5]}...{pat[-5:]}?"
    )
    set_password("siesta", "github_pat", pat)
    logger.success("GitHub PAT set. You can now use `siesta docs init`.")


@project_app.command(name="quickstart")
def quickstart_project(
    as_app: bool = False,
    as_pkg: bool = False,
    precommit: bool | None = None,
    docs: bool | None = None,
    deps: bool | None = None,
    docs_path: str = "./docs",
    as_main_deps: bool | None = None,
    overwrite: bool = False,
    with_defaults: bool = True,
    branch: str = "main",
    contents: str = "src/siesta/boilerplate",
    local: bool = False,
):
    """Start a ``uv``-based Python project from scratch, with initial project structure and docs.

    Overall:

    * Initializes a new ``uv`` project with ``$ uv init``.
    * Installs recommended dependencies with ``$ uv add --dev [...]``.
    * Initializes a new Sphinx project at the specified path as per ``$ siesta
      docs init``.
    * Initializes pre-commit hooks with ``$ uv run pre-commit install``.

    .. note::

        The default behavior is to initialize the project as a library (with a package
        structure within a ``src/`` folder). Use the ``--as-app`` flag to initialize the
        project as an app (just a script file to start with) or ``--as-pkg`` to initialize
        as a package (with a package structure in the root directory).

    .. important::

        Using ``--with-defaults`` will trust the defaults and skip all prompts:

        - Install recommended dependencies.
        - Initialize pre-commit hooks.
        - Initialize the docs.

    .. important::

        If you generate the docs, (with ``--docs`` or ``--with-defaults``) parameters
        like ``--deps`` and ``--as_main_deps`` will passed to the ``siesta docs init``
        command so it may be worth checking ``$ siesta docs init --help``.

    Parameters
    ----------
    as_app : bool, optional
        Whether to initialize the project as an app (just a script file to start with).
    as_pkg : bool, optional
        Whether to initialize the project as a package (with a package structure in the root directory).
    precommit : bool, optional
        Whether to install pre-commit hooks, by default ``None`` (i.e. prompt the user).
    docs : bool, optional
        Whether to initialize the docs, by default ``None`` (i.e. prompt the user).
    deps : bool, optional
        Whether to install dependencies (dev &? docs), by default ``None`` (i.e. prompt the user).
    docs_path : str, optional
        Where to build the docs, by default ``./docs``.
    as_main_deps : bool, optional
        Whether to include docs dependencies in the main dependencies, by default
        ``None`` (i.e. prompt the user).
    overwrite : bool, optional
        Whether to overwrite existing files (if any). Will be passed to ``siesta
        docs init``.
    with_defaults : bool, optional
        Whether to trust the defaults and skip all prompts.
    branch : str, optional
        The branch to fetch the static files from.
    contents : str, optional
        The path to the static files in the repository.
    local : bool, optional
        Use local boilerplate docs assets instead of fetching from the repository.
        May update to outdated contents so avoid using this option.
    """
    if as_app and as_pkg:
        logger.abort("Cannot use both --as-app and --as-pkg flags.")

    has_uv = bool(run_command(["uv", "--version"]))
    if not has_uv:
        logger.abort(
            "uv not found. Please install it first -> https://docs.astral.sh/uv/getting-started/installation/"
        )

    if with_defaults:
        if precommit is not None:
            logger.warning("Ignoring precommit argument because of --with-defaults.")
        precommit = True
        if docs is not None:
            logger.warning("Ignoring docs argument because of --with-defaults.")
        docs = True
        if deps is not None:
            logger.warning("Ignoring deps argument because of --with-defaults.")
        deps = True
        if as_main_deps is not None:
            logger.warning("Ignoring as_main_deps argument because of --with-defaults.")
        as_main_deps = False

    has_uv_lock = Path("uv.lock").exists()
    if not has_uv_lock:
        cmd = ["uv", "init"]
        if as_app:
            # Initialize as app (no src/ directory)
            pass
        elif as_pkg:
            # Initialize as package (package structure in root directory)
            cmd.append("--package")
        else:
            # Initialize as library (package structure in src/ directory)
            cmd.append("--lib")

        initialized = run_command(cmd)
        if initialized is False:
            logger.abort("Failed to initialize the project.")
        logger.success("Project initialized with uv.")
    else:
        logger.info("Project already initialized with uv.")

    if deps is None:
        deps = logger.confirm("Would you like to install recommended dependencies?")
    if deps:
        dev_deps = load_deps()["dev"]
        # Check which dependencies are already installed
        missing_deps = []
        for dep in dev_deps:
            try:
                __import__(dep.split("[")[0])  # Handle cases like package[extra]
            except ImportError:
                missing_deps.append(dep)

        if missing_deps:
            installed = run_command(["uv", "add", "--dev"] + missing_deps)
            if installed is False:
                logger.abort("Failed to install the dev dependencies.")
            logger.success("Dev dependencies installed.")
        else:
            logger.info("All dev dependencies already installed.")

    if precommit is None:
        precommit = logger.confirm(
            "Would you like to update & install pre-commit hooks?"
        )
    if precommit:
        write_or_update_pre_commit_file()
        pre_commit_installed = run_command(["uv", "run", "pre-commit", "install"])
        if pre_commit_installed is False:
            logger.abort("Failed to install pre-commit hooks.")
        logger.success("Pre-commit hooks installed.")

    if docs is None:
        docs = logger.confirm("Would you like to initialize the docs?")
    if docs:
        init_docs(
            path=docs_path,
            as_main_deps=as_main_deps,
            overwrite=overwrite,
            deps=deps,
            with_defaults=with_defaults,
            branch=branch,
            contents=contents,
            local=local,
        )
    logger.info(
        "Ask Victor if you want to automatically build and deploy the docs to ReadTheDocs."
    )
    logger.success("Done.")


@docs_app.command(name="build")
def build_docs(path: str = "./docs"):
    """Build your docs.

    Equivalent to running ``$ cd docs && make clean && make html``.

    Parameters
    ----------
    path : str, optional
        The path to your documentation folder.
    """
    path = resolve_path(path)
    if not path.exists():
        logger.abort(f"Path not found: {path}", exit=1)
    make = path / "Makefile"
    if not make.exists():
        logger.abort(f"Makefile not found in {path}.", exit=1)
    commands = [
        ["make", "clean"],
        ["make", "html"],
    ]
    with_uv = Path("uv.lock").exists()
    if with_uv:
        commands = [["uv", "run"] + command for command in commands]
    for command in commands:
        with logger.loading(f"Running {' '.join(command)}..."):
            result = run_command(command, cwd=str(path), check=False)
        if result.returncode != 0:
            logger.error(result.stderr)
            logger.abort("Failed to build the docs.")
        print(result.stdout)
    logger.info(
        "Ask Victor if you want to automatically build and deploy the docs to ReadTheDocs."
    )
    logger.success(f"Local docs built in {path / 'build/html/index.html'}")


@docs_app.command(name="watch")
def watch_docs(
    path: str = "./docs", patterns: str = r".+/src/.+\.py;.+/source/.+\.rst"
):
    """Automatically build the docs when source files matching the given patterns are changed.

    Files must be accessible down the directory you run the command from.

    Files in the ``/autoapi/`` folder are not watched so that the intermediate
    files generated by AutoAPI do not trigger a continuous rebuild.

    Parameters
    ----------
    path : str, optional
        The path to your documentation folder.
    patterns : str, optional
        The patterns to watch for changes, separated by ``;``.
    """
    build_docs(path)
    patterns = [p.strip() for p in patterns.split(";")]
    abd = AutoBuildDocs(patterns, build_docs, path=path)
    observer = Observer()
    observer.schedule(abd, path=".", recursive=True)
    observer.start()
    here = Path().resolve()
    logger.info(f"Watching {here}. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
    print()
    logger.warning("Watching stopped. Bye bye 👋")
