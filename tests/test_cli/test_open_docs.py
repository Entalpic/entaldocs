from unittest.mock import patch

import pytest

from siesta.cli import app


@pytest.mark.parametrize("platform", ["Darwin", "Windows", "Linux"])
def test_open_docs(module_test_path, capture_output, platform, monkeypatch):
    """Test opening the docs in the default browser."""
    monkeypatch.chdir(module_test_path)

    with capture_output() as output:
        with patch("siesta.cli.platform.system") as mock_system:
            mock_system.return_value = platform

            # Only mock os.startfile for Windows
            if platform == "Windows":
                with patch("siesta.cli.os.startfile", create=True) as mock_startfile:
                    with patch("siesta.cli.subprocess.call") as mock_call:
                        app(["docs", "open"])
                        mock_startfile.assert_called_once_with(
                            str(
                                module_test_path
                                / "docs"
                                / "build"
                                / "html"
                                / "index.html"
                            )
                        )
                        # subprocess.call should not be called on Windows
                        mock_call.assert_not_called()
            else:
                # For Darwin and Linux, only mock subprocess.call
                with patch("siesta.cli.subprocess.call") as mock_call:
                    app(["docs", "open"])
                    if platform == "Darwin":
                        mock_call.assert_called_once_with(
                            (
                                "open",
                                str(
                                    module_test_path
                                    / "docs"
                                    / "build"
                                    / "html"
                                    / "index.html"
                                ),
                            )
                        )
                    else:  # Linux
                        mock_call.assert_called_once_with(
                            (
                                "xdg-open",
                                str(
                                    module_test_path
                                    / "docs"
                                    / "build"
                                    / "html"
                                    / "index.html"
                                ),
                            )
                        )
    assert "Opening" in output.getvalue()
    assert "index.html" in output.getvalue()
