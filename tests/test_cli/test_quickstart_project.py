# Copyright 2025 Entalpic
from pathlib import Path

from siesta.cli import app


def test_quickstart_project(tmp_path_chdir, capture_output):
    """Test project quickstart command creates expected project structure."""

    with capture_output() as output:
        app(["project", "quickstart", "--with-defaults", "--local"])

    assert "Failed to build the docs" not in output.getvalue()

    project_name = tmp_path_chdir.name

    # Check project structure
    assert Path(tmp_path_chdir, "src").exists()
    assert Path(tmp_path_chdir, "docs").exists()
    assert Path(tmp_path_chdir, ".pre-commit-config.yaml").exists()
    assert Path(tmp_path_chdir, ".readthedocs.yaml").exists()
    assert Path(tmp_path_chdir, "uv.lock").exists()
    assert Path(tmp_path_chdir, "tests").exists()
    assert Path(tmp_path_chdir, ".github").exists()
    assert Path(tmp_path_chdir, ".github", "workflows", "test.yml").exists()
    assert Path(tmp_path_chdir, "src", project_name).exists()
    assert Path(tmp_path_chdir, "src", project_name, "__init__.py").exists()


def test_quickstart_project_as_app(tmp_path_chdir, capture_output):
    """Test project quickstart --as-app creates app structure instead of library."""

    with capture_output() as output:
        app(["project", "quickstart", "--as-app", "--with-defaults", "--local"])

    assert "Failed to build the docs" not in output.getvalue()
    # Should not have src directory for app
    assert not Path(tmp_path_chdir, "src").exists()
    # But should still have docs
    assert Path(tmp_path_chdir, "docs").exists()


def test_quickstart_project_as_pkg(tmp_path_chdir, capture_output):
    """Test project quickstart --as-pkg creates package structure in root directory."""

    with capture_output() as output:
        app(["project", "quickstart", "--as-pkg", "--with-defaults", "--local"])

    assert "Failed to build the docs" not in output.getvalue()
    assert (tmp_path_chdir / "src").exists()
    assert (tmp_path_chdir / "src" / tmp_path_chdir.name).exists()
