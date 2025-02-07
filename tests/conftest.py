import os
import sys
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from subprocess import run
from unittest.mock import patch

import pytest

os.environ["PYTHONBREAKPOINT"] = "ipdb.set_trace"


class MockKeyring:
    """Mock keyring that always returns a fake PAT."""

    def get_password(self, service, username):
        return "fake-github-pat-for-testing"

    def set_password(self, service, username, password):
        pass


@pytest.fixture(autouse=True)
def mock_keyring():
    """Mock the entire keyring system to use our fake implementation.

    This fixture is automatically used in all tests.
    """
    mock_kr = MockKeyring()
    with (
        patch("keyring.get_keyring", return_value=mock_kr),
        patch("keyring.set_password", mock_kr.set_password),
        patch("keyring.get_password", mock_kr.get_password),
    ):
        yield mock_kr


@pytest.fixture
def capture_output():
    @contextmanager
    def c():
        """Context manager to capture stdout for testing.

        Example
        -------

        .. code-block:: python

            with capture_output() as output:
                app(["show-deps"])
            assert "numpy" in output.getvalue()

        Returns
        -------
        StringIO
            The captured stdout buffer.
        """
        stdout = StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = stdout
            yield stdout
        finally:
            sys.stdout = old_stdout

    return c


def tree() -> str:
    """Print a recursive directory tree, ignoring .venv directory.

    Mostly to debug tests.

    Returns
    -------
    str
        A string representation of the directory tree.
    """

    def _tree(path: Path, prefix: str = "", is_last: bool = True) -> str:
        if path.name == ".venv":
            return ""

        # Prepare the current line
        result = prefix + ("└── " if is_last else "├── ") + path.name + "\n"

        if path.is_dir():
            # Get all visible items (no hidden files)
            items = sorted([x for x in path.iterdir() if not x.name.startswith(".")])
            # Filter out .venv
            items = [x for x in items if x.name != ".venv"]

            # Handle children
            for i, item in enumerate(items):
                is_last_item = i == len(items) - 1
                new_prefix = prefix + ("    " if is_last else "│   ")
                result += _tree(item, new_prefix, is_last_item)

        return result

    return _tree(Path.cwd())


@pytest.fixture
def temp_project_with_git_and_remote(tmp_path):
    """Create a temporary project directory with a basic structure.

    Function-scoped to ensure a fresh directory for each test.
    """
    # Create a basic src structure
    src = tmp_path / "src" / "mypackage"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("# Test package")

    # Create a basic git repo to test URL detection
    run(["git", "init"], cwd=str(tmp_path))
    run(
        ["git", "remote", "add", "origin", "git@github.com:test/test.git"],
        cwd=str(tmp_path),
    )

    return tmp_path
