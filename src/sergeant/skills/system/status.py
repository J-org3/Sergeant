from __future__ import annotations
import shutil
import asyncio
import psutil
from ..base import skill

@skill(
    name="get_system_status",
    description="Gets the current system status: CPU, RAM, temperature, and disk usage.",
    category="system",
)
async def get_system_status() -> dict:
    return await asyncio.to_thread(_collect_status_sync)

def _collect_status_sync() -> dict:
    disk = shutil.disk_usage("/")
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_used_mb": round(psutil.virtual_memory().used / 1024 / 1024, 1),
        "disk_used_percent": round(disk.used / disk.total * 100, 1),
        "cpu_temp_celsius": _read_cpu_temp(),
        "uptime_seconds": _get_uptime(),
    }

def _read_cpu_temp() -> float | None:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(int(f.read().strip()) / 1000, 1)
    except (FileNotFoundError, ValueError):
        return None

def _get_uptime() -> float:
    try:
        with open("/proc/uptime") as f:
            return round(float(f.read().split()[0]), 1)
    except FileNotFoundError:
        return 0.0