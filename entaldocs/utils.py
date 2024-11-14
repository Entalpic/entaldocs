import json
import sys
from filecmp import cmp as compare_files
from os.path import expandvars, relpath
from pathlib import Path
from shutil import copy2, copytree
from subprocess import run
from tempfile import TemporaryDirectory

from github import Github, UnknownObjectException
from github.Auth import Token
from github.Repository import Repository
from keyring import get_password
from rich import print

from entaldocs.logger import Logger

logger = Logger("entaldocs")
"""A logger to log messages to the console."""


def get_user_pat():
    """Get the GitHub Personal Access Token (PAT) from the user.

    Returns
    -------
    str
        The GitHub Personal Access Token (PAT).
    """
    return get_password("entaldocs", "github_pat")


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


def _copy_not_overwrite(src: str | Path, dest: str | Path):
    """Private function to copy a file, backing up the destination if it exists.

    To be used by :func:`copy_defaults_folder` and :func:`~shutil.copytree` to update files recursively
    without overwriting existing files.

    Inspiration: `Stackoverflow <https://stackoverflow.com/a/78638812/3867406>`_

    Parameters
    ----------
    src : str | Path
        The path to the src file.
    dest : str | Path
        The path to copy the target file to.
    """
    if Path(dest).exists() and not compare_files(src, dest, shallow=False):
        backed_up = backup(dest)
        logger.warning(f"Backing up {dest} to {backed_up}")
    copy2(src, dest)


def backup(path: Path) -> Path:
    """Backup a file by copying it to the same directory with a .bak extension.

    If the file already exists, it will be copied with a .bak.1, .bak.2, etc. extension.

    Parameters
    ----------
    path : Path
        The path to backup the target files to.
    overwrite : bool
        Whether to overwrite the files if they already exist.

    Returns
    -------
    Path
        The path to the backup file.
    """
    src = resolve_path(path)
    dest = src.parent / f"{src.name}.bak"
    if dest.exists():
        b = 1
        while (dest := src.parent / f"{src.name}.bak.{b}").exists():
            b += 1
    copy2(src, dest)
    return dest


def copy_boilerplate(
    dest: Path,
    overwrite: bool,
    branch: str = "main",
    content_path: str = "boilerplate",
):
    """Copy the target files to the specified path.

    Parameters
    ----------
    dest : Path
        The path to copy the target files to.
    overwrite : bool
        Whether to overwrite the files if they already exist.
    branch: str
        The branch to fetch the files from, by default ``"main"``.
    content_path: str
        The directory or file to fetch from the repository
    """
    with TemporaryDirectory() as tmpdir:
        fetch_github_files(content_path=content_path, branch=branch, dir=tmpdir)
        dest = resolve_path(dest)

        assert dest.exists(), f"Destination folder not found: {dest}"
        copytree(
            tmpdir,
            dest,
            dirs_exist_ok=True,
            copy_function=copy2 if overwrite else _copy_not_overwrite,
        )


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


def make_empty_folders(dest: Path):
    """Make the static and build folders in the target folder.

    Parameters
    ----------
    dest : Path
        The path to make the empty folders in.
    """
    dest = resolve_path(dest)

    assert dest.exists(), f"Destination folder not found: {dest}"

    (dest / "build").mkdir(parents=True, exist_ok=True)
    (dest / "source/_static").mkdir(parents=True, exist_ok=True)
    (dest / "source/_templates").mkdir(parents=True, exist_ok=True)


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


def discover_packages(dest: Path, with_defaults: str) -> str:
    """Discover packages in the current directory.

    Directories will be returned relatively to the conf.py file in the documentation
    folder as a list of strings.

    Parameters
    ----------
    dest : Path
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
            logger.abort(f"Package not found: {p}", exit=1)

    ref = dest / "source"
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


def overwrite_docs_files(dest: Path, with_defaults: bool):
    """Overwrite the conf.py file with the project name.

    Parameters
    ----------
    dest : Path
        The path to the conf.py file.
    with_defaults : bool
        Whether to trust the defaults and skip all prompts.
    """
    dest = resolve_path(dest)
    # get the packages to list in autoapi_dirs
    packages = discover_packages(dest, with_defaults)
    # get project name from $CWD or user prompt
    project = get_project_name(with_defaults)
    # get repo URL from git or user prompt
    url = get_repo_url(with_defaults)

    # setup conf.py based on project name and packages
    conf_py = dest / "source/conf.py"
    assert conf_py.exists(), f"conf.py not found: {dest}"
    conf_text = conf_py.read_text()
    conf_text = conf_text.replace("$PROJECT_NAME", project)
    conf_text = conf_text.replace("autoapi_dirs = []", f"autoapi_dirs = {packages}")
    conf_py.write_text(conf_text)

    # setup autoapi index.rst based on project name and repo URL
    index_rst = dest / "source/_templates/autoapi/index.rst"
    assert index_rst.exists(), f"autoapi/index.rst not found: {dest}"
    index_text = index_rst.read_text()
    index_text = index_text.replace("$PROJECT_NAME", project)
    index_text = index_text.replace("$PROJECT_URL", url)
    index_rst.write_text(index_text)


def search_contents(
    repo: Repository, contents_path: str, branch: str = "main"
) -> list[tuple[str, str]]:
    """Get the (deep) contents of a directory.

    Parameters
    ----------
    repo : Repository
        The repository to get the contents from.
    contents_path : str
        The path to the directory to get the contents of.
    branch : str, optional
        The branch to fetch the files from, by default ``"main"``.

    Returns
    -------
    list[tuple[str, bytes]]
        The list of tuples containing the file path and content as ``(path, bytes content)``.

    """
    contents = repo.get_contents(contents_path, ref=branch)
    data = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            logger.clear_line()
            print(f"Getting contents of '{file_content.path}'", end="\r")
            data.append((file_content.path, file_content.decoded_content))
    logger.clear_line()
    logger.info(f"Downloaded contents of '{repo.html_url}/{contents_path}'")
    return data


def fetch_github_files(content_path: str, branch: str = "main", dir: str = ".") -> Path:
    """Download a file or directory from a GitHub repository.

    Parameters
    ----------
    content_path : str
        The directory or file to fetch from the repository
    branch : str, optional
        The branch to fetch the files from, by default ``"main"``.
    dir : str, optional
        The directory to save the files to, by default ``"."``.

    Returns
    -------
    Path
        The path to the temporary folder containing the files.
    """
    pat = get_user_pat()
    if not pat:
        logger.abort(
            "GitHub Personal Access Token (PAT) not found. Run 'entaldocs set-github-pat' to set it.",
            exit=1,
        )
        sys.exit(1)
    auth = Token(pat)
    g = Github(auth=auth)
    repo = g.get_repo("entalpic/entaldocs")
    try:
        contents = search_contents(repo, content_path, branch)
    except UnknownObjectException:
        branches = repo.get_branches()
        has_branch = any(b.name == branch for b in branches)
        if not has_branch:
            logger.abort(f"Branch not found: {branch}", exit=1)
        else:
            logger.abort(f"Could not find repository contents: {content_path}", exit=1)
        return

    data = search_contents(contents, [])
    base_dir = resolve_path(dir)
    for name, content in data:
        path = Path(base_dir) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
