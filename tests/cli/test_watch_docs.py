from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from watchdog.observers import Observer

from siesta.cli import app
from siesta.utils import AutoBuild


def test_watch_docs_path_not_found(capture_output):
    """Test watch_docs fails when path doesn't exist."""
    with pytest.raises(SystemExit) as exc_info:
        with capture_output() as output:
            app(["docs watch", "--path", "nonexistent/path"])
        assert "Path not found" in output.getvalue()

    assert exc_info.value.code == 1


def test_watch_docs_observer_setup(module_test_path, monkeypatch, capture_output):
    """Test watch_docs sets up observer correctly."""
    monkeypatch.chdir(module_test_path)

    mock_observer = Mock(spec=Observer)
    mock_observer_instance = mock_observer.return_value

    with (
        patch("siesta.cli.Observer", mock_observer),
        patch("time.sleep", side_effect=KeyboardInterrupt),
    ):
        with capture_output() as output:
            app(["docs watch"])

    # Verify observer was started
    assert mock_observer_instance.start.called
    # Verify observer was stopped after KeyboardInterrupt
    assert mock_observer_instance.stop.called
    assert mock_observer_instance.join.called
    # Verify watching message
    assert "Watching stopped" in output.getvalue()


def test_autobuild_on_modified(module_test_path, monkeypatch):
    """Test AutoBuild handler processes file changes correctly."""
    monkeypatch.chdir(module_test_path)

    # Create mock build command
    mock_build = Mock()

    # Create AutoBuild instance with test patterns
    patterns = [".+/src/.+\\.py", ".+/source/.+\\.rst"]
    handler = AutoBuild(patterns, mock_build, "docs")

    # Test Python source file change
    mock_event = Mock()
    mock_event.src_path = str(Path("src/mypackage/test.py"))
    handler.on_modified(mock_event)
    assert mock_build.called
    mock_build.reset_mock()

    # Test RST file change in source
    mock_event.src_path = str(Path("docs/source/index.rst"))
    handler.on_modified(mock_event)
    assert mock_build.called
    mock_build.reset_mock()

    # Test file change in autoapi folder (should not trigger build)
    mock_event.src_path = str(Path("docs/source/autoapi/index.rst"))
    handler.on_modified(mock_event)
    assert not mock_build.called
    mock_build.reset_mock()

    # Test non-matching file change
    mock_event.src_path = str(Path("random/file.txt"))
    handler.on_modified(mock_event)
    assert not mock_build.called


def test_watch_docs_custom_patterns(module_test_path, monkeypatch, capture_output):
    """Test watch_docs accepts custom patterns."""
    monkeypatch.chdir(module_test_path)

    mock_observer = Mock(spec=Observer)
    custom_patterns = "custom/*.py;other/*.rst"

    with (
        patch("siesta.cli.Observer", mock_observer),
        patch("time.sleep", side_effect=KeyboardInterrupt),
    ):
        with capture_output():
            app(["docs watch", "--patterns", custom_patterns])

    # Verify observer was scheduled with handler using custom patterns
    schedule_call = mock_observer.return_value.schedule.call_args[0]
    handler = schedule_call[0]
    assert isinstance(handler, AutoBuild)
    assert handler.regexes == [p.strip() for p in custom_patterns.split(";")]


def test_watch_docs_keyboard_interrupt_handling(
    module_test_path, monkeypatch, capture_output
):
    """Test watch_docs handles keyboard interrupt gracefully."""
    monkeypatch.chdir(module_test_path)

    mock_observer = Mock(spec=Observer)

    with (
        patch("siesta.cli.Observer", mock_observer),
        patch("time.sleep", side_effect=KeyboardInterrupt),
    ):
        with capture_output() as output:
            app(["docs watch"])

    # Verify graceful shutdown messages
    assert "Watching stopped" in output.getvalue()
    assert "👋" in output.getvalue()

    # Verify observer cleanup
    mock_observer_instance = mock_observer.return_value
    assert mock_observer_instance.stop.called
    assert mock_observer_instance.join.called
