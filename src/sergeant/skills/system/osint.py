from __future__ import annotations
import asyncio
import logging
import re
import httpx

try:
    import shodan
except ImportError:
    shodan = None

from ..base import skill
from sergeant.config import get_settings

logger = logging.getLogger(__name__)

TARGET_RE = re.compile(r"^[a-zA-Z0-9.\-:]+$")

VALID_TECHNIQUES = {
    "dns_recon",
    "whois_lookup",
    "wayback_history",
    "shodan_host",
    "banner_detection",
}

def _validate_target(target: str) -> str | None:
    if not target or len(target) > 253 or not TARGET_RE.match(target):
        return None
    return target

async def _run(cmd: list[str], timeout: float = 20.0) -> dict:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return {"error": f"Command exceeded {timeout}s timeout"}

    return {
        "returncode": proc.returncode,
        "stdout": stdout.decode(errors="replace").strip(),
        "stderr": stderr.decode(errors="replace").strip(),
    }

@skill(
    name="osint_recon",
    description=(
        "Executes an OSINT reconnaissance technique on a domain or IP. "
        "Available techniques: dns_recon (DNS records via dig), "
        "whois_lookup (domain WHOIS), "
        "wayback_history (historical snapshots in Wayback Machine), "
        "shodan_host (Shodan info about an IP, requires configured API key), "
        "banner_detection (real service fingerprinting via nmap -sV, detects fake services on standard ports). "
        "The target must be a valid domain or IP, without paths or extra parameters. "
        "Requires user confirmation before execution."
    ),
    requires_confirmation=True,
    category="osint",
)
async def osint_recon(technique: str, target: str) -> dict:
    if technique not in VALID_TECHNIQUES:
        return {
            "error": f"Technique '{technique}' not recognized.",
            "available_techniques": sorted(VALID_TECHNIQUES),
        }

    clean_target = _validate_target(target)
    if clean_target is None:
        return {"error": f"Target '{target}' is not a valid domain or IP."}

    logger.info("osint_recon: technique=%s target=%s", technique, clean_target)

    if technique == "dns_recon":
        result = await _run(["dig", "-t", "any", clean_target])
        result["technique"] = "dns_recon"
        return result

    if technique == "whois_lookup":
        result = await _run(["whois", clean_target])
        result["technique"] = "whois_lookup"
        return result

    if technique == "wayback_history":
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://web.archive.org/cdx/search/cdx",
                    params={
                        "url": f"{clean_target}*",
                        "output": "json",
                        "fl": "timestamp,original,statuscode",
                        "limit": "30",
                    },
                )
                resp.raise_for_status()
            return {"technique": "wayback_history", "snapshots": resp.json()}
        except httpx.HTTPError as exc:
            return {"error": f"Error querying Wayback Machine: {exc}"}

    if technique == "shodan_host":
        settings = get_settings()
        if not settings.shodan_configured:
            return {"error": "SHODAN_API_KEY not configured in .env. Add it to use this technique."}
        if shodan is None:
            return {"error": "The 'shodan' library is not installed."}
            
        try:
            api = shodan.Shodan(settings.shodan_api_key)
            host = api.host(clean_target)
            return {
                "technique": "shodan_host",
                "ip": host.get("ip_str"),
                "org": host.get("org"),
                "os": host.get("os"),
                "ports": host.get("ports"),
                "hostnames": host.get("hostnames"),
                "vulns": list(host.get("vulns", [])),
            }
        except shodan.APIError as exc:
            return {"error": f"Shodan error: {exc}"}

    if technique == "banner_detection":
        result = await _run(["nmap", "-sV", "--top-ports", "20", clean_target], timeout=60.0)
        result["technique"] = "banner_detection"
        return result

    return {"error": "Technique not implemented"}