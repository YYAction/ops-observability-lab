from pathlib import Path

from log_scan import LogLine, scan_lines

def test_scan_finds_errors():
    lines = [
        LogLine(Path("app.log"), 1, "ERROR database timeout"),
        LogLine(Path("app.log"), 2, "INFO normal"),
    ]

    counter, hits = scan_lines(lines, ["ERROR"], case_sensitive=False)

    assert counter["ERROR"] == 1
    assert len(hits) == 1
    assert hits[0][0].text == "ERROR database timeout"
    assert hits[0][1] == ["ERROR"]

def test_scan_empty_input():
    counter, hits = scan_lines([], ["ERROR"], case_sensitive=False)

    assert counter["ERROR"] == 0
    assert hits == []
