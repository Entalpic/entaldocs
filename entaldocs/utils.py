import json
from os.path import expandvars, relpath
from pathlib import Path
from shutil import copytree
from subprocess import run

from rich import print

from entaldocs.logger import Logger

logger = Logger()
"""A logger to log messages to the console."""


def resolve_path(path: str | Path) -> Path:
    """Resolve a path and expand environment variables.

    Parameters
    ----------
    path : str | Path
        The path to resolve.

    Returns:
    --------
    Path
        The resolved path.
    """
    return Path(expandvars(path)).expanduser().resolve()


def load_deps() -> list[str]:
    """Load dependencies from the |dependenciesjson|_ file.


    Returns
    -------
    list[str]
        The dependencies to load.

    .. |dependenciesjson| replace:: ``dependencies.json``
    .. _dependenciesjson: ../../../dependencies.json
    .. include 3x "../" because we need to reach /dependencies.json from /autoapi/entaldocs/utils/index.html
    """
    path = resolve_path(__file__).parent / "dependencies.json"
    return json.loads(path.read_text())


def copy_defaults_folder(to: Path):
    """Copy the target files to the specified path.

    Parameters
    ----------
    to : Path
        The path to copy the target files to.
    """
    target = resolve_path(__file__).parent / "__defaults"
    to = resolve_path(to)

    assert to.exists(), f"Destination folder not found: {to}"

    copytree(target, to, dirs_exist_ok=True)


def install_dependencies(uv: bool, dev: bool):
    """Install dependencies for the docs.

    Parameters
    ----------
    uv : bool
        Whether to install using ``uv`` or ``pip install``.
    dev : bool
        If using ``uv``, whether to install as dev dependencies.
    """
    cmd = ["uv", "add"] if uv else ["python", "-m", "pip", "install"]
    if dev:
        cmd.append("--dev")
    cmd.extend(load_deps())
    output = run(cmd, check=True)
    print(output.stdout or "")


def make_empty_folders(to: Path):
    """Make the static and build folders in the target folder.

    Parameters
    ----------
    to : Path
        The path to make the empty folders in.
    """
    to = resolve_path(to)

    assert to.exists(), f"Destination folder not found: {to}"

    (to / "build").mkdir(parents=True, exist_ok=True)
    (to / "source/_static").mkdir(parents=True, exist_ok=True)
    (to / "source/_templates").mkdir(parents=True, exist_ok=True)


def get_project_name(with_defaults) -> str:
    """Get the current project's name from the user.

    Prompts the user for the project name, with the default being the current
    directory's name.

    Parameters
    ----------
    with_defaults : bool
        Whether to trust the defaults and skip all prompts.

    Returns
    -------
    str
        The project name.
    """
    default = resolve_path(".").name
    return default if with_defaults else logger.prompt("Project name", default=default)


def discover_packages(to: Path, with_defaults: str) -> str:
    """Discover packages in the current directory.

    Directories will be returned relatively to the conf.py file in the documentation
    folder as a list of strings.

    Parameters
    ----------
    to : Path
        The path to the documentation folder
    with_defaults : bool
        Whether to trust the defaults and skip all prompts.

    Returns
    -------
    str:
        The discovered packages as a JSON-dumped list of strings.
    """
    start = "."
    if (resolve_path(start) / "src").exists():
        start = "src"
    packages = [
        p for p in Path(start).iterdir() if p.is_dir() and (p / "__init__.py").exists()
    ]
    if not packages and not with_defaults:
        user_packages = logger.prompt(
            "No packages found. Enter relative package paths separated by commas"
        )
        packages = [resolve_path(p.strip()) for p in user_packages.split(",")]
    for p in packages:
        if not p.exists():
            logger.abort(f"Package not found: {p}")

    ref = to / "source"
    packages = [relpath(p, ref) for p in packages]

    return json.dumps([str(p) for p in packages])


def get_repo_url(with_defaults: bool) -> str:
    """Get the repository URL from the user.

    Prompts the user for the repository URL.

    Parameters
    ----------
    with_defaults : bool
        Whether to trust the defaults and skip all prompts.

    Returns
    -------
    str
        The repository URL.
    """
    url = ""
    try:
        ssh_url = run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        html_url = "https://github.com/" + ssh_url.split(":")[-1].replace(".git", "")
        url = (
            html_url
            if with_defaults
            else logger.prompt("Repository URL", default=html_url)
        )
    except Exception:
        url = url if with_defaults else logger.prompt("Repository URL", default=url)
    finally:
        return url


def overwrite_docs_files(to: Path, with_defaults: bool):
    """Overwrite the conf.py file with the project name.

    Parameters
    ----------
    to : Path
        The path to the conf.py file.
    with_defaults : bool
        Whether to trust the defaults and skip all prompts.
    """
    to = resolve_path(to)
    # get the packages to list in autoapi_dirs
    packages = discover_packages(to, with_defaults)
    # get project name from $CWD or user prompt
    project = get_project_name(with_defaults)
    # get repo URL from git or user prompt
    url = get_repo_url(with_defaults)

    # setup conf.py based on project name and packages
    conf_py = to / "source/conf.py"
    assert conf_py.exists(), f"conf.py not found: {to}"
    conf_text = conf_py.read_text()
    conf_text = conf_text.replace("$PROJECT_NAME", project)
    conf_text = conf_text.replace("autoapi_dirs = []", f"autoapi_dirs = {packages}")
    conf_py.write_text(conf_text)

    # setup autoapi index.rst based on project name and repo URL
    index_rst = to / "source/_templates/autoapi/index.rst"
    assert index_rst.exists(), f"autoapi/index.rst not found: {to}"
    index_text = index_rst.read_text()
    index_text = index_text.replace("$PROJECT_NAME", project)
    index_text = index_text.replace("$PROJECT_URL", url)
    index_rst.write_text(index_text)
