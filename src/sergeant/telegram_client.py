import logging
from typing import Any

import httpx

from sergeant.config import Settings

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.telegram_api_base

    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_to_message_id: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }

        if reply_to_message_id is not None:
            payload["reply_to_message_id"] = reply_to_message_id

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.base_url}/sendMessage",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def set_webhook(self) -> dict[str, Any]:
        payload = {
            "url": self.settings.public_webhook_url,
            "secret_token": self.settings.telegram_webhook_secret,
            "drop_pending_updates": False,
            "allowed_updates": ["message"],
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.base_url}/setWebhook",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def delete_webhook(self, drop_pending_updates: bool = False) -> dict[str, Any]:
        payload = {
            "drop_pending_updates": drop_pending_updates,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.base_url}/deleteWebhook",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def get_webhook_info(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{self.base_url}/getWebhookInfo")
            response.raise_for_status()
            return response.json()
