#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
log_scan_exporter.py

将 log_scan.py 的扫描能力包装成 Prometheus exporter。
每隔 SCAN_INTERVAL 秒扫描一次日志，把结果暴露在 :8000/metrics。
"""

import os
import time
import threading

from prometheus_client import start_http_server, Gauge, Counter
from log_scan import find_log_files, collect_recent_lines, scan_lines

# ── 配置，全部通过环境变量控制 ──────────────────────────────
LOG_PATH = os.environ.get("LOG_PATH", "/logs")
SCAN_INTERVAL = int(os.environ.get("SCAN_INTERVAL", "30"))
KEYWORDS = os.environ.get("KEYWORDS", "ERROR,脱机,死锁").split(",")
SCAN_LINES = int(os.environ.get("SCAN_LINES", "4000"))
LOG_PATTERN = os.environ.get("LOG_PATTERN", "Logs_*.txt*")

# ── Prometheus 指标定义 ────────────────────────────────────
# Gauge: 最近一次扫描的命中数（按关键字分标签）
scan_alerts = Gauge(
    "logscan_scan_alerts",
    "Alerts found in the most recent scan",
    ["keyword"],
)

# Gauge: 最近一次扫描的总命中数
scan_alerts_total = Gauge(
    "logscan_scan_alerts_total",
    "Total alerts found in the most recent scan",
)

# Gauge: 最近一次扫描覆盖了多少行
scan_lines_scanned = Gauge(
    "logscan_scan_lines_scanned",
    "Number of lines scanned in the most recent scan",
)

# Gauge: 最近一次扫描的时间戳（unix seconds）
scan_timestamp = Gauge(
    "logscan_scan_timestamp",
    "Timestamp of the most recent scan",
)

# Counter: 累计执行了多少次扫描
scans_completed = Counter(
    "logscan_scans_completed_total",
    "Total number of scans completed",
)


def do_scan():
    """执行一次扫描，更新所有指标。"""
    files = find_log_files(LOG_PATH, LOG_PATTERN)

    if not files:
        print(f"[exporter] 未找到日志文件: path={LOG_PATH} pattern={LOG_PATTERN}")
        scan_alerts_total.set(0)
        scan_lines_scanned.set(0)
        scan_timestamp.set(time.time())
        scans_completed.inc()
        return

    recent = collect_recent_lines(files, SCAN_LINES)
    counter, _hits = scan_lines(recent, KEYWORDS, case_sensitive=False)

    # 更新指标
    total = sum(counter.values())
    scan_alerts_total.set(total)
    scan_lines_scanned.set(len(recent))
    scan_timestamp.set(time.time())
    scans_completed.inc()

    for kw in KEYWORDS:
        scan_alerts.labels(keyword=kw).set(counter.get(kw, 0))

    print(
        f"[exporter] 扫描完成: {len(files)} 个文件, "
        f"{len(recent)} 行, {total} 条告警"
    )


def scan_loop():
    """后台循环：每隔 SCAN_INTERVAL 秒扫描一次。"""
    while True:
        try:
            do_scan()
        except Exception as e:
            print(f"[exporter] 扫描出错: {e}")
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    port = int(os.environ.get("EXPORTER_PORT", "8000"))
    print(f"[exporter] 启动 HTTP 服务: :{port}/metrics")
    print(f"[exporter] 扫描目标: {LOG_PATH} (pattern={LOG_PATTERN})")
    print(f"[exporter] 关键字: {KEYWORDS}")
    print(f"[exporter] 扫描间隔: {SCAN_INTERVAL}s, 扫描行数: {SCAN_LINES}")

    # 启动 /metrics HTTP 服务
    start_http_server(port)

    # 主线程跑扫描循环
    scan_loop()
