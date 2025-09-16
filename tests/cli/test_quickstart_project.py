from pathlib import Path

from siesta.cli import app


def test_quickstart_project(tmp_path, monkeypatch, capture_output):
    """Test project quickstart command creates expected project structure."""
    monkeypatch.chdir(tmp_path)

    with capture_output() as output:
        app(["project quickstart", "--with-defaults", "--local"])

    assert "Failed to build the docs" not in output.getvalue()

    # Check project structure
    assert Path(tmp_path, "src").exists()
    assert Path(tmp_path, "docs").exists()
    assert Path(tmp_path, ".pre-commit-config.yaml").exists()
    assert Path(tmp_path, ".readthedocs.yaml").exists()
    assert Path(tmp_path, "uv.lock").exists()


def test_quickstart_project_as_app(tmp_path, monkeypatch, capture_output):
    """Test project quickstart --as-app creates app structure instead of library."""
    monkeypatch.chdir(tmp_path)

    with capture_output() as output:
        app(["project quickstart", "--as-app", "--with-defaults", "--local"])

    assert "Failed to build the docs" not in output.getvalue()
    # Should not have src directory for app
    assert not Path(tmp_path, "src").exists()
    # But should still have docs
    assert Path(tmp_path, "docs").exists()


def test_quickstart_project_as_pkg(tmp_path, monkeypatch, capture_output):
    """Test project quickstart --as-pkg creates package structure in root directory."""
    monkeypatch.chdir(tmp_path)

    with capture_output() as output:
        app(["project quickstart", "--as-pkg", "--with-defaults", "--local"])

    assert "Failed to build the docs" not in output.getvalue()
    assert (tmp_path / "src").exists()
    assert (tmp_path / "src" / tmp_path.name).exists()
