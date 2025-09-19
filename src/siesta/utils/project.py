from pathlib import Path
from textwrap import dedent

from siesta.utils.common import get_pyver, logger, safe_dump


def write_test_actions_config() -> None:
    """
    Write the test actions config to the ``.github/workflows/test.yml`` file.

    Basically this will allow you to run tests automatically on Github on any PR or push to the main branch.
    """
    github_dir = Path(".github")
    workflows_dir = github_dir / "workflows"
    if workflows_dir.exists():
        logger.warning("Workflows directory already exists. Skipping.")
        return
    workflows_dir.mkdir(parents=True, exist_ok=True)
    test_config = {
        "name": "Tests",
        "on": {
            "pull_request": "",
            "push": {
                "branches": ["main"],
            },
        },
        "jobs": {
            "test-install": {
                "runs-on": "ubuntu-latest",
                "strategy": {"matrix": {"python-version": [get_pyver()]}},
                "steps": [
                    {
                        "uses": "actions/checkout@v4",
                    },
                    {
                        "name": "Set up Python ${{ matrix.python-version }}",
                        "uses": "actions/setup-python@v5",
                        "with": {"python-version": "${{ matrix.python-version }}"},
                    },
                    {
                        "name": "Install uv",
                        "run": "curl -LsSf https://astral.sh/uv/install.sh | sh",
                    },
                    {
                        "name": "Install dependencies",
                        "run": "uv sync",
                    },
                ],
            },
            "test-pytest": {
                "runs-on": "ubuntu-latest",
                "strategy": {"matrix": {"python-version": [get_pyver()]}},
                "steps": [
                    {
                        "uses": "actions/checkout@v4",
                    },
                    {
                        "name": "Set up Python ${{ matrix.python-version }}",
                        "uses": "actions/setup-python@v5",
                        "with": {"python-version": "${{ matrix.python-version }}"},
                    },
                    {
                        "name": "Install uv",
                        "run": "curl -LsSf https://astral.sh/uv/install.sh | sh",
                    },
                    {
                        "name": "Install dependencies",
                        "run": "uv sync",
                    },
                    {
                        "name": "Run tests",
                        "run": "uv run pytest",
                    },
                ],
            },
        },
    }
    safe_dump(test_config, workflows_dir / "test.yml")
    logger.info("Test actions config written.")


def write_tests_infra(project_name: str):
    """Write the tests infrastructure to the ``tests/`` directory.

    This will create a ``test_import.py`` file that will test that the project can be imported.

    Parameters
    ----------
    project_name : str
        The name of the project.
    """
    tests_dir = Path("tests")
    if tests_dir.exists():
        logger.warning("Tests directory already exists. Skipping.")
        return
    tests_dir.mkdir(parents=True, exist_ok=True)
    test_example = dedent(f'''
    import pytest
    
    @pytest.fixture(autouse=True)
    def mock_variable():
        """Mock some variable."""
        yield 42

    def test_variable(mock_variable):
        """Test the variable."""
        assert mock_variable == 42

    def test_import():
        """Test the project's import."""
        import {project_name}  # noqa: F401
    ''')
    (tests_dir / "test_import.py").write_text(test_example)

    logger.info("Tests infra written.")


def add_ipdb_as_debugger():
    """Set ``ipdb`` as default debugger to the project.

    This will set ``ipdb`` as default debugger when calling ``breakpoint()`` by setting the
    ``PYTHONBREAKPOINT`` environment variable to ``ipdb.set_trace``.
    """
    inits = list(Path("src/").glob("**/__init__.py"))
    if not inits:
        logger.warning("No __init__.py files found. Skipping ipdb debugger.")
        return

    first_init = sorted(
        [(i, len(str(i).split("/"))) for i in inits], key=lambda x: x[1]
    )[0][0]

    first_init.write_text(
        first_init.read_text()
        + dedent(
            """
            try:
                import os

                import ipdb  # noqa: F401

                # set ipdb as default debugger when calling `breakpoint()`
                os.environ["PYTHONBREAKPOINT"] = "ipdb.set_trace"
            except ImportError:
                print(
                    "`ipdb` not available.",
                    "Consider adding it to your dev stack for a smoother debugging experience.",
                )
            """
        )
    )
    logger.info("ipdb added as debugger.")
