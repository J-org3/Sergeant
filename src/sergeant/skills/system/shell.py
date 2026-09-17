from __future__ import annotations
import asyncio
import logging
import shlex
from ..base import skill

logger = logging.getLogger(__name__)

ALLOWED_COMMANDS: dict[str, str] = {
    "system_status": "systemctl status Sergeant --no-pager",
    "disk_usage": "df -h",
    "memory_usage": "free -h",
    "cpu_temp": "vcgencmd measure_temp",
    "uptime": "uptime",
    "list_services": "systemctl list-units --type=service --state=running --no-pager",
    "network_interfaces": "ip -brief addr",
}

@skill(
    name="run_shell_command",
    description=(
        "Executes a predefined administration command on the Raspberry Pi. "
        "Available commands are: " + ", ".join(ALLOWED_COMMANDS.keys()) + ". "
        "Requires user confirmation before execution."
    ),
    requires_confirmation=True,
    category="system",
)
async def run_shell_command(command_key: str) -> dict:
    command = ALLOWED_COMMANDS.get(command_key)
    if command is None:
        return {
            "error": f"'{command_key}' is not in the whitelist.",
            "allowed_commands": list(ALLOWED_COMMANDS.keys()),
        }

    logger.info("Executing whitelisted command: %s", command_key)
    args = shlex.split(command)
    
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15.0)
    except asyncio.TimeoutError:
        proc.kill()
        return {"error": f"Command '{command_key}' exceeded 15s timeout"}

    return {
        "command_key": command_key,
        "returncode": proc.returncode,
        "stdout": stdout.decode(errors="replace").strip(),
        "stderr": stderr.decode(errors="replace").strip(),
    }