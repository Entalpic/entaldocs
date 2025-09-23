# Copyright 2025 Entalpic
from pathlib import Path


def test_copyrights():
    src = Path(__file__).resolve().parent.parent
    no_copyrights = []
    for file in (
        list(src.rglob("*.py"))
        + list(src.rglob("*.rst"))
        + list(src.rglob("*.yaml"))
        + list(src.rglob("*.yml"))
    ):
        if ".venv" in str(file):
            continue
        first_line = file.read_text().split("\n")[0]
        if "Copyright" not in first_line or "Entalpic" not in first_line:
            no_copyrights.append(
                f"Copyright not found in {file} ; first line: {first_line}"
            )
    assert len(no_copyrights) == 0, "\n".join(no_copyrights)
