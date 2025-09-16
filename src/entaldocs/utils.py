# Copyright 2025 Entalpic
"""
A set of utilities to help with the ``entaldocs`` CLI and the
initialization of Entalpic-style documentation projects.
"""

import importlib
import json
import re
import sys
from filecmp import cmp as compare_files
from os.path import expandvars, relpath
from pathlib import Path
from shutil import copy2, copytree
from subprocess import CalledProcessError, run
from tempfile import TemporaryDirectory

from github import Github, UnknownObjectException
from github.Auth import Token
from github.Repository import Repository
from keyring import get_password
from rich import print
from ruamel.yaml import YAML
from watchdog.events import FileSystemEvent, RegexMatchingEventHandler

from entaldocs.logger import Logger

logger = Logger("entaldocs")
"""A logger to log messages to the console."""
ROOT = importlib.resources.files("entaldocs")
"""The root directory of the ``entaldocs`` package."""


def safe_dump(data, file, **kwargs):
    """Uses ``ruamel.yaml`` to dump data to a file.

    Parameters
    ----------
    data : dict
        The data to dump to the file.
    file : str | Path | IO
        The file to dump the data to.
    """
    handle = file
    if isinstance(file, str):
        handle = open(file, "w")
    else:
        handle = file

    yaml = YAML(typ="rt", pure=True)
    yaml.default_flow_style = False
    yaml.dump(data, handle, **kwargs)
    if isinstance(file, str):
        handle.close()


def safe_load(file):
    """Uses ``ruamel.yaml`` to load data from a file.

    Parameters
    ----------
    file : str | Path | IO
        The file to load the data from.
    """
    handle = file
    if isinstance(file, str):
        handle = open(file, "r")
    yaml = YAML(typ="safe", pure=True)
    return yaml.load(handle)


def run_command(
    cmd: list[str], check: bool = True, cwd: str | Path | None = None
) -> str | bool:
    """Run a command in the shell.

    Parameters
    ----------
    cmd : list[str]
        The command to run.
    check : bool, optional
        Whether to raise an error if the command fails, by default ``True``.
    cwd : str | Path | None, optional
        The working directory to run the command in, by default ``None``.

    Returns
    -------
    str | bool
        The result of the command.
    """
    try:
        return run(
            cmd,
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=cwd,
        )
    except CalledProcessError as e:
        logger.error(e.stderr)
        return False


def get_user_pat():
    """Get the GitHub Personal Access Token (PAT) from the user.

    Returns
    -------
    str
        The GitHub Personal Access Token (PAT).
    """
    return get_password("entaldocs", "github_pat")


def get_pyver():
    """Get the Python version from the user.

    Returns
    -------
    str
        The Python version.
    """
    python_version_file = Path(".python-version")
    if python_version_file.exists():
        return python_version_file.read_text().strip()
    if run_command(["which", "uv"]):
        # e.g. "Python 3.12.1"
        full_version = run_command(["uv", "run", "python", "--version"]).stdout.strip()
        version = full_version.split()[1]
        major, minor, _ = version.split(".")
        return f"{major}.{minor}"


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
    path = ROOT / "dependencies.json"
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
    content_path: str = "src/entaldocs/boilerplate",
    include_files_regex: str = ".*",
    local: bool = False,
):
    """Copy the target files to the specified path.

    You can specify specific files to include using a regex pattern,
    used (approximately) as follows:

    .. code-block:: python

        with TemporaryDirectory() as tmpdir:
            keep_file = re.findall(regex, str(file.relative_to(tmpdir)))

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
    include_files_regex: str
        A regex pattern to include only files that match the pattern with :func:`re.findall`.
    """
    with TemporaryDirectory() as tmpdir:
        if local:
            # use local boilerplate:
            # copy the boilerplate folder to the tmpdir
            copytree(
                ROOT / content_path.replace("src/entaldocs/", ""),
                Path(tmpdir),
                dirs_exist_ok=True,
            )
        else:
            fetch_github_files(branch=branch, content_path=content_path, dir=tmpdir)
        tmpdir = Path(tmpdir)
        if include_files_regex:
            for f in tmpdir.rglob("*"):
                fn = str(f.relative_to(tmpdir))
                if f.is_file() and not re.match(include_files_regex, fn):
                    f.unlink()

        dest = resolve_path(dest)

        assert dest.exists(), f"Destination folder not found: {dest}"
        copytree(
            tmpdir,
            dest,
            dirs_exist_ok=True,
            copy_function=copy2 if overwrite else _copy_not_overwrite,
        )


def update_conf_py(dest: Path, branch: str = "main"):
    """Update the ``conf.py`` file with the latest content from the boilerplate.

    Parameters
    ----------
    dest : Path
        The path to the ``conf.py`` file.
    branch : str, optional
        Which remote branch to get ``conf.py`` from, by default ``"main"``
    """
    with TemporaryDirectory() as tmpdir:
        fetch_github_files(
            branch=branch,
            content_path="src/entaldocs/boilerplate/source/conf.py",
            dir=tmpdir,
        )
        tmpdir = Path(tmpdir)
        src = tmpdir / "conf.py"
        dest = resolve_path(dest / "source/conf.py")
        assert dest.exists(), f"Destination file (conf.py) not found: {dest}"
        start_pattern = "# :entaldocs: <update>"
        end_pattern = "# :entaldocs: </update>"

        # load the source and destination files contents
        src_content = src.read_text()
        dest_content = dest.read_text()
        # get the content between the start and end patterns in the source file
        pattern = f"{start_pattern}(.+){end_pattern}"
        incoming = re.search(pattern, src_content, flags=re.DOTALL)
        if not incoming:
            return
        incoming = incoming.group(1)

        # replace the content between the start and end patterns in the destination file
        replacement = f"{start_pattern}{incoming}{end_pattern}"
        if re.search(pattern, dest_content, flags=re.DOTALL):
            # pattern exists, replace it
            dest_content = re.sub(pattern, replacement, dest_content, flags=re.DOTALL)
        else:
            # pattern does not exist, add it
            dest_content += f"\n{replacement}\n"

        if not dest_content.endswith("\n"):
            dest_content += "\n"

        # write the updated content to the destination file
        dest.write_text(dest_content)


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
    cmd.extend(load_deps()["docs"])
    # capture error and output
    output = run_command(cmd)
    if output is not False:
        print(output.stdout.strip())


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
    if not packages:
        packages = [Path(".")]
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
        ssh_url = run_command(
            ["git", "config", "--get", "remote.origin.url"]
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
    index_text = index_text.replace("$PROJECT_URL", url or " URL TO BE SET ")
    index_rst.write_text(index_text)


def search_contents(
    repo: Repository, branch: str = "main", content_path: str = "boilerplate"
) -> list[tuple[str, str]]:
    """Get the (deep) contents of a directory.

    Parameters
    ----------
    repo : Repository
        The repository to get the contents from.
    content_path : str
        The path to the directory to get the contents of.
    branch : str, optional
        The branch to fetch the files from, by default ``"main"``.

    Returns
    -------
    list[tuple[str, bytes]]
        The list of tuples containing the file path and content as
        ``(path, bytes content)``.

    """
    contents = repo.get_contents(content_path, ref=branch)
    if not isinstance(contents, list):
        contents = [contents]

    # If we don't adjust the content path, fetching a folder will include the full content
    # path and the files will be copied to the wrong location:
    # eg: if we fetch boilerplate/ and the content is boilerplate/docs/source/conf.py
    #     the file will be copied to "boilerplate/docs/source/conf.py" instead of
    #     "docs/source/conf.py"
    # so we'll remove the hierarchy of the folder from the path
    # trying to download a file
    extra_path = content_path
    if re.match(r".+\.\w+", extra_path.split("/")[-1]):
        # we'll just keep the file name
        extra_path = "/".join(extra_path.split("/")[:-1])
    else:
        # trying to download a folder
        if not extra_path.endswith("/"):
            # we'll remove the hierarchy of the folder from the path
            extra_path = extra_path + "/"

    data = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path, ref=branch))
        else:
            logger.clear_line()
            print(f"Getting contents of '{file_content.path}'", end="\r")
            # adjust file path
            new_relative_path = file_content.path.replace(extra_path, "")
            if new_relative_path.startswith("/"):
                new_relative_path = new_relative_path[1:]
            data.append(
                (
                    new_relative_path,
                    file_content.decoded_content,
                )
            )
    logger.clear_line()
    logger.info(f"Downloaded contents of '{repo.html_url}/{content_path}'")
    return data


def fetch_github_files(
    branch: str = "main",
    content_path: str = "src/entaldocs/boilerplate",
    dir: str = ".",
) -> Path:
    """Download a file or directory from a GitHub repository and write it to ``dir``.

    Parameters
    ----------
    branch : str, optional
        The branch to fetch the files from, by default ``"main"``.
    content_path : str
        The directory or file to fetch from the repository
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
        contents = search_contents(repo, branch=branch, content_path=content_path)
    except UnknownObjectException:
        branches = repo.get_branches()
        has_branch = any(b.name == branch for b in branches)
        if not has_branch:
            logger.abort(f"Branch not found: {branch}", exit=1)
        else:
            logger.abort(
                f"Could not find repository contents: {content_path} on branch {branch}",
                exit=1,
            )
        return

    base_dir = resolve_path(dir)
    for name, content in contents:
        path = Path(base_dir) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def write_or_update_pre_commit_file() -> None:
    """Write the pre-commit file to the current directory."""
    pre_commit = Path(".pre-commit-config.yaml")
    ref = ROOT / "precommits.yaml"
    if pre_commit.exists():
        # Load existing config
        with open(pre_commit, "r") as f:
            current = safe_load(f)

        # Load reference config
        with open(ref, "r") as f:
            reference = safe_load(f)

        # Update existing config with reference repos
        if not isinstance(current, dict):
            current = {}
        if not isinstance(reference, dict):
            reference = {}
        if "repos" not in current:
            current["repos"] = []
        if "repos" not in reference:
            reference["repos"] = []
        current_repos = {repo["repo"]: repo for repo in current["repos"]}
        for repo in reference["repos"]:
            current_repos[repo["repo"]] = repo

        current["repos"] = list(current_repos.values())

        # Write updated config
        safe_dump(current, pre_commit)
        logger.info("pre-commit file updated.")
        return

    # Copy reference file if no existing config
    copy2(ref, pre_commit)
    logger.info("pre-commit file written.")
    return


def write_rtd_config() -> None:
    """Write the ReadTheDocs configuration file to the current directory."""
    rtd = Path(".readthedocs.yaml")
    if rtd.exists():
        logger.warning("ReadTheDocs file already exists. Skipping.")
        return
    pyver = get_pyver()
    config = {
        "version": 2,
        "build": {
            "os": "ubuntu-22.04",
            "tools": {"python": pyver},
            "commands": [
                "asdf plugin add uv",
                "asdf install uv latest",
                "asdf global uv latest",
                "uv sync",
                "uv run sphinx-build -M html docs/source $READTHEDOCS_OUTPUT",
            ],
        },
    }

    safe_dump(config, rtd)
    logger.info("ReadTheDocs file written.")


def has_python_files(path: Path = Path(".")) -> bool:
    """Check if there are any Python files in the given path or its subdirectories.

    Parameters
    ----------
    path : Path, optional
        The path to check for Python files, by default current directory.

    Returns
    -------
    bool
        True if Python files are found, False otherwise.
    """
    # Look for .py files, excluding common test directories and virtual environments
    exclude_dirs = {".venv", "venv", ".tox", ".eggs", "build", "dist"}
    for p in path.rglob("*.py"):
        # Check if any parent directory is in exclude_dirs
        if not any(x in exclude_dirs for x in p.parts):
            return True
    return False


class AutoBuild(RegexMatchingEventHandler):
    """Automatically build the docs when they are changed.

    Parameters
    ----------
    regexes : list[str]
        The regexes to match against the file paths.
    build_command : list[str]
        The command to run to build the docs.
    path : str
        The path to the docs folder.
    """

    def __init__(self, regexes: list[str], build_command: list[str], path: str):
        super().__init__(regexes=regexes)
        self.build_command = build_command
        self.path = path

    def on_modified(self, event: FileSystemEvent):
        """File modified event handler.

        Runs the build command if the file is a source file that needs to be built.

        Parameters
        ----------
        event : FileSystemEvent
            The event to handle.
        """
        path = event.src_path
        suffix = Path(path).suffix
        is_autoapi_rst = "/source/" in path and "/autoapi/" in path and suffix == ".rst"
        is_docs_py = str(self.path) in path and suffix == ".py"

        dont_run = is_autoapi_rst or is_docs_py

        if not dont_run:
            logger.info(f"Building docs because {path} was modified.")
            self.build_command(self.path)
