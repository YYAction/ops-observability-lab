# tests/test_log_scan.py
from log_scan import scan_lines  # 或者你的函数名

def test_scan_finds_errors():
    lines = ["ERROR database timeout", "INFO normal"]
    # 根据你 scan_lines 的实际返回值写断言

def test_scan_empty_input():
    result = scan_lines([])
    # 验证空输入不报错