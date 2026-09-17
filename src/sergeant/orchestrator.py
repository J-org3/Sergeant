import logging
from dataclasses import dataclass

from sergeant.config import get_settings
from sergeant.models.router import ConfirmationRequired, ModelRouter

logger = logging.getLogger(__name__)


@dataclass
class IncomingMessage:
    user_id: int
    chat_id: int
    message_id: int
    text: str
    username: str | None = None
    first_name: str | None = None


class SergeantOrchestrator:
    def __init__(self):
        self.settings = get_settings()
        self.model_router = ModelRouter(self.settings)
        self.commands = {
            "/start": self._cmd_start,
            "/ping": lambda m: "pong",
            "/whoami": self._cmd_whoami,
            "/model": self._cmd_model,
            "/clear": self._cmd_clear,
        }

    async def handle_message(self, message: IncomingMessage) -> str:
        logger.info(
            "Message received | user_id=%s | chat_id=%s | username=%s | text=%r",
            message.user_id,
            message.chat_id,
            message.username,
            message.text,
        )
        text = message.text.strip()

        if text in self.commands:
            return self.commands[text](message)

        if text == "/confirm":
            return await self._handle_confirmation(message.chat_id, approved=True)
        if text == "/cancel":
            return await self._handle_confirmation(message.chat_id, approved=False)

        force_provider = None
        if text.startswith("/local "):
            force_provider = "ollama"
            text = text.removeprefix("/local ").strip()
        elif text.startswith("/azure "):
            force_provider = "azure"
            text = text.removeprefix("/azure ").strip()

        return await self._generate_and_format(text, message.chat_id, force_provider)

    async def _handle_confirmation(self, chat_id: int, approved: bool) -> str:
        result = await self.model_router.resume_after_confirmation(chat_id, approved=approved)
        return format_model_response(result.text, result.provider, result.model)

    async def _generate_and_format(
        self,
        prompt: str,
        chat_id: int,
        force_provider: str | None = None,
    ) -> str:
        try:
            result = await self.model_router.generate(
                prompt,
                force_provider=force_provider,
                chat_id=chat_id,
            )
            return format_model_response(result.text, result.provider, result.model)
        except ConfirmationRequired as exc:
            args_preview = ", ".join(f"{k}={v!r}" for k, v in exc.tool_args.items())
            return (
                "⚠️ The agent wants to execute a sensitive action:\n\n"
                f"`{exc.tool_name}({args_preview})`\n\n"
                "Reply /confirm to execute it or /cancel to discard it."
            )

    def _cmd_start(self, msg: IncomingMessage) -> str:
        return (
            "Sergeant online.\n\n"
            "Telegram webhook connected.\n"
            "FastAPI running.\n"
            "Cloudflare Tunnel active.\n"
            "Model router and memory initialized."
        )

    def _cmd_whoami(self, msg: IncomingMessage) -> str:
        return (
            "Telegram Data:\n\n"
            f"user_id: {msg.user_id}\n"
            f"chat_id: {msg.chat_id}\n"
            f"username: {msg.username}\n"
            f"first_name: {msg.first_name}"
        )

    def _cmd_model(self, msg: IncomingMessage) -> str:
        return (
            "Model Configuration:\n\n"
            f"primary: {self.settings.model_primary}\n"
            f"fallback: {self.settings.model_fallback}\n"
            f"azure_configured: {self.settings.azure_configured}\n"
            f"azure_deployment: {self.settings.azure_openai_deployment or '(empty)'}\n"
            f"ollama_model: {self.settings.ollama_model}"
        )

    def _cmd_clear(self, msg: IncomingMessage) -> str:
        self.model_router.memory.clear_history(msg.chat_id)
        return "🧠 Session memory cleared. The context has been reset."


def format_model_response(text: str, provider: str, model: str) -> str:
    if not text:
        text = "(no response)"
    return (
        f"{text}\n\n"
        f"---\n"
        f"provider: {provider}\n"
        f"model: {model}"
    )