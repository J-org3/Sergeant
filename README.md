<div align="center">
  <img src="assets/banner.png" alt="Sergeant AI Banner" width="100%">
</div>

# Sergeant: Edge-Native AI Agent

<div align="center">
  <img src="assets/icon.png" alt="Sergeant Icon" width="120" height="120">
  <p><em>Autonomous, tool-calling AI agent built for Edge devices and Linux servers.</em></p>
</div>

Sergeant is an autonomous, tool-calling AI agent built with a **FastAPI** backend and connected directly to **Telegram**. It is designed to act as an on-call system administrator and OSINT reconnaissance assistant on low-power edge nodes (such as a Raspberry Pi 4B) or remote Linux servers.

---

## Architecture Overview

* **Hybrid Model Routing:** Evaluates prompts against a primary cloud endpoint (Azure OpenAI) and automatically falls back to a locally hosted GGUF model via Ollama if connection drops or latency spikes occur.
* **Persistent Edge Memory:** Features a local SQLite transaction store that maintains conversational continuity and function call context across restarts without heavy vector database memory overhead.
* **Human-in-the-Loop Interruption:** Sensitive operations (command execution, intrusive scans) pause the pipeline and request explicit authorization (`/confirm` or `/cancel`) via Telegram.
* **Dynamic Skill Discovery:** Scans the `skills` package at startup using runtime inspection to register typed tool schemas directly into the LLM context.

---

## Platform Compatibility & Linux Dependencies

Sergeant's core engine (FastAPI, SQLite memory, Telegram webhook, and LLM orchestration) is **cross-platform** and runs on Linux, macOS, and Windows. 

However, the included **system skills rely directly on native Linux binaries**:

| Tool / Skill | Required Host Binary | Platform Note |
| :--- | :--- | :--- |
| `osint_recon (dns_recon)` | `dig` (`dnsutils` / `bind-utils`) | Linux / Unix native CLI |
| `osint_recon (whois_lookup)` | `whois` | Linux / Unix package |
| `osint_recon (banner_detection)` | `nmap` | Must be present in system `PATH` |
| `run_shell_command` | Linux Coreutils (`df`, `free`, `ip`, `systemctl`) | Requires a systemd-based Linux host |
| `get_system_status` | `/proc/uptime`, `vcgencmd` | Temperature reading is optimized for Raspberry Pi thermal zones |

> **Running on non-Linux systems:** If deploying on Windows or macOS for development, the core chat and API-based skills (Wayback Machine, Shodan) will function as expected, but subshell commands and hardware telemetry will raise missing-binary or path errors.

---

## Installation & Setup

### 1. System Dependencies

* **Linux (Debian / Ubuntu / Raspberry Pi OS):**
  Install required tools for native system telemetry and OSINT skills:
  ```bash
  sudo apt-get update && sudo apt-get install -y git python3-venv dnsutils whois nmap
  ```

* **Windows (PowerShell Development):**
  Core agent routing, memory, Telegram webhooks, and API-driven tools (Wayback Machine, Shodan) run natively on Windows.
  *(Optional: If you want `nmap` or `whois` support on Windows, install them via Chocolatey or Scoop: `choco install nmap whois`).*

---

### 2. Clone & Virtual Environment

* **Linux / macOS:**
  ```bash
  git clone https://github.com/J-org3/Sergeant.git
  cd Sergeant
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

* **Windows (PowerShell):**
  ```powershell
  git clone https://github.com/J-org3/Sergeant.git
  cd Sergeant
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

---

### 3. Environment Configuration

Copy the sample environment file:

* **Linux / macOS:** `cp .env.example .env`
* **Windows (PowerShell):** `Copy-Item .env.example .env`

Edit `.env` with your actual credentials:
* Set `TELEGRAM_BOT_TOKEN` and define your secret webhook path.
* Specify your personal Telegram ID in `ALLOWED_TELEGRAM_USER_IDS` to restrict unauthorized access at the webhook layer.
* Provide Azure OpenAI and/or local Ollama connection parameters.

---

### 4. Running Locally

Execute the FastAPI application runner:

```bash
python run.py
```

---

## Production Deployment (systemd + Cloudflare Tunnel)

To keep Sergeant active 24/7 on an edge node behind NAT:

1. Expose port `8000` securely using a Cloudflare Tunnel:
```bash
cloudflared tunnel run <your-tunnel-name>
```

2. Create the systemd service definition:
```bash
sudo nano /etc/systemd/system/sergeant.service
```

3. Add the following unit configuration (adjust working directory and paths):
```ini
[Unit]
Description=Sergeant Autonomous Agent
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Sergeant
Environment="PATH=/home/pi/Sergeant/.venv/bin"
ExecStart=/home/pi/Sergeant/.venv/bin/python run.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

4. Reload systemd and start the daemon:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now sergeant.service
```

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.