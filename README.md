<div align="center">
  <img src="./assets/banner.jpg" alt="Sergeant AI Banner" width="100%">
</div>

# Sergeant: Edge-Native AI Agent

<div align="center">
  <img src="./assets/icon.png" alt="Sergeant Icon" width="120" height="120">
  <p><em>Autonomous, tool-calling AI agent built for the Edge.</em></p>
</div>

Sergeant is an autonomous AI agent designed to run continuously on low-power edge devices (like a Raspberry Pi 4B) or Linux servers. Built with a FastAPI backend and integrated directly with Telegram, it bridges the gap between local OSINT/SysAdmin tasks and Large Language Models.

## 🧠 Architecture & Features

Sergeant operates on a highly modular architecture focusing on security, persistence, and fallback routing:

* **Hybrid Model Router:** Dynamically routes inference between an Azure OpenAI endpoint (`gpt-4o-mini`) and a local LLM via Ollama (e.g., `Llama-3.1-8B`). If the cloud provider times out or fails, it automatically falls back to local execution.
* **Tool Calling (Skills):** Uses an auto-discovering registry for Python functions. The agent can interact with the host OS, perform DNS/WHOIS recons, and query Shodan natively.
* **Security & Sandboxing:** Destructive or sensitive tools trigger an asynchronous interrupt, sending a Telegram confirmation prompt (`/confirm` or `/cancel`) to the administrator before `shlex`-secured execution.
* **Persistent Edge Memory:** Utilizes a lightweight SQLite transaction engine to maintain persistent conversational context without the RAM overhead of heavy vector databases.

## 🖥️ Platform Compatibility

While the core AI routing, OSINT skills, and Telegram webhook architecture are **100% cross-platform** (Windows, macOS, Linux), Sergeant is optimized as an **Edge-Native** application. 

Specific system skills (like `get_system_status` and `run_shell_command`) use Linux/Raspberry Pi native commands (e.g., `systemctl`, `vcgencmd`). If you run this on Windows or macOS, those specific hardware skills will need minor adjustments, but the rest of the agent will function perfectly.

## 🛠️ Tech Stack
* **Core:** Python 3.10+, FastAPI, Uvicorn, SQLite3
* **AI Providers:** `openai` (Azure), `httpx` (Ollama REST API)
* **Integrations:** Telegram Webhook API, Shodan API, Linux Subprocess (`asyncio`)

## ⚙️ Capabilities (Skills Registry)

* `osint_recon`: Network scanning, Wayback Machine archives, DNS/WHOIS mapping.
* `get_system_status`: Real-time hardware telemetry (CPU temp, RAM, Disk usage) fetched asynchronously.
* `run_shell_command`: Whitelisted administration commands for server maintenance via safe `shlex` execution.

---

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone [https://github.com/yourusername/Sergeant-v1.git](https://github.com/yourusername/Sergeant-v1.git)
cd Sergeant-v1