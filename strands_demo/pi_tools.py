"""Raspberry Pi telemetry tools.

These ``@tool``-decorated functions are reused by both
``pi_telemetry_agent.py`` (single agent) and ``pi_multi_agent.py``
(multi-agent orchestrator).

Dependencies: Python standard library + ``strands-agents``."""

import re
import shutil
import subprocess
import time
from pathlib import Path

from strands import tool


def _run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, timeout=5).strip()


@tool
def pi_info() -> dict:
    """Return basic identification for this Raspberry Pi: model, hostname,
    kernel, and OS pretty name."""
    model = Path("/proc/device-tree/model").read_text(errors="ignore").strip("\x00 \n")
    hostname = _run(["hostname"])
    kernel = _run(["uname", "-r"])
    os_pretty = ""
    for line in Path("/etc/os-release").read_text().splitlines():
        if line.startswith("PRETTY_NAME="):
            os_pretty = line.split("=", 1)[1].strip().strip('"')
            break
    return {
        "model": model,
        "hostname": hostname,
        "kernel": kernel,
        "os": os_pretty,
    }


@tool
def cpu_temperature() -> dict:
    """Return the current SoC temperature in degrees Celsius."""
    out = _run(["vcgencmd", "measure_temp"])
    match = re.search(r"([\d.]+)", out)
    return {"temperature_c": float(match.group(1)) if match else None, "raw": out}


@tool
def cpu_usage() -> dict:
    """Return overall CPU utilization sampled over a short interval (percent
    busy, 0-100), plus 1/5/15 minute load averages."""

    def _snapshot() -> list[int]:
        with open("/proc/stat") as f:
            parts = f.readline().split()
        return [int(x) for x in parts[1:8]]

    a = _snapshot()
    time.sleep(0.5)
    b = _snapshot()
    idle = (b[3] + b[4]) - (a[3] + a[4])
    total = sum(b) - sum(a)
    pct = 100.0 * (total - idle) / total if total else 0.0
    load1, load5, load15 = (float(x) for x in Path("/proc/loadavg").read_text().split()[:3])
    return {
        "cpu_percent": round(pct, 1),
        "load_avg_1m": load1,
        "load_avg_5m": load5,
        "load_avg_15m": load15,
    }


@tool
def memory_usage() -> dict:
    """Return total, used, and available RAM in megabytes."""
    info: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, _, rest = line.partition(":")
        info[key.strip()] = int(rest.strip().split()[0])  # values in kB
    total_mb = info["MemTotal"] / 1024
    avail_mb = info["MemAvailable"] / 1024
    used_mb = total_mb - avail_mb
    return {
        "total_mb": round(total_mb, 1),
        "used_mb": round(used_mb, 1),
        "available_mb": round(avail_mb, 1),
        "used_percent": round(100 * used_mb / total_mb, 1),
    }


@tool
def disk_usage(path: str = "/") -> dict:
    """Return disk usage statistics for the filesystem containing ``path``.

    Args:
        path: Any path on the target filesystem. Defaults to ``/``.
    """
    total, used, free = shutil.disk_usage(path)
    gb = 1024**3
    return {
        "path": path,
        "total_gb": round(total / gb, 2),
        "used_gb": round(used / gb, 2),
        "free_gb": round(free / gb, 2),
        "used_percent": round(100 * used / total, 1),
    }


@tool
def uptime() -> dict:
    """Return how long this Pi has been running."""
    seconds = float(Path("/proc/uptime").read_text().split()[0])
    days, rem = divmod(int(seconds), 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    return {
        "seconds": int(seconds),
        "pretty": f"{days}d {hours}h {minutes}m",
    }


@tool
def throttling_status() -> dict:
    """Report whether the Pi is currently throttled or has been throttled
    since boot (under-voltage, frequency capping, etc.) via vcgencmd."""
    raw = _run(["vcgencmd", "get_throttled"])
    code = int(raw.split("=")[1], 16)
    flags = {
        "under_voltage_now": bool(code & 0x1),
        "freq_capped_now": bool(code & 0x2),
        "throttled_now": bool(code & 0x4),
        "soft_temp_limit_now": bool(code & 0x8),
        "under_voltage_occurred": bool(code & 0x10000),
        "freq_capped_occurred": bool(code & 0x20000),
        "throttled_occurred": bool(code & 0x40000),
        "soft_temp_limit_occurred": bool(code & 0x80000),
    }
    return {"raw": raw, "code": hex(code), **flags}
