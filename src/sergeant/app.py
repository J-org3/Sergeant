import logging
from typing import Any

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

from sergeant.config import get_settings
from sergeant.orchestrator import IncomingMessage, SergeantOrchestrator
from sergeant.telegram_client import TelegramClient

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sergeant",
    version="0.2.0",
)

telegram = TelegramClient(settings)
orchestrator = SergeantOrchestrator()


@app.get("/")
async def root():
    return {
        "message": "Sergeant online",
        "status": "ok",
        "version": "0.2.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "Sergeant",
        "env": settings.sergeant_env,
    }


@app.get("/telegram/webhook-info")
async def telegram_webhook_info():
    return await telegram.get_webhook_info()


@app.post(settings.telegram_webhook_path)
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> JSONResponse:
    if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        logger.warning("Webhook rechazado: secret token inválido")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    update = await request.json()
    background_tasks.add_task(process_telegram_update, update)

    return JSONResponse({"ok": True})


async def process_telegram_update(update: dict[str, Any]) -> None:
    try:
        message_payload = extract_message(update)

        if message_payload is None:
            logger.info("Update ignorado: no contiene mensaje de texto compatible")
            return

        allowed_ids = settings.allowed_telegram_user_ids
        if allowed_ids and message_payload.user_id not in allowed_ids:
            logger.warning(
                "Usuario no autorizado | user_id=%s | username=%s",
                message_payload.user_id,
                message_payload.username,
            )
            await telegram.send_message(
                chat_id=message_payload.chat_id,
                text="No autorizado.",
            )
            return

        response_text = await orchestrator.handle_message(message_payload)

        await telegram.send_message(
            chat_id=message_payload.chat_id,
            text=response_text,
            reply_to_message_id=message_payload.message_id,
        )

    except Exception:
        logger.exception("Error procesando update de Telegram")


def extract_message(update: dict[str, Any]) -> IncomingMessage | None:
    message = update.get("message")
    if not message:
        return None

    text = message.get("text")
    if not text:
        return None

    chat = message.get("chat", {})
    from_user = message.get("from", {})

    chat_id = chat.get("id")
    user_id = from_user.get("id")
    message_id = message.get("message_id")

    if chat_id is None or user_id is None or message_id is None:
        return None

    return IncomingMessage(
        user_id=int(user_id),
        chat_id=int(chat_id),
        message_id=int(message_id),
        text=str(text),
        username=from_user.get("username"),
        first_name=from_user.get("first_name"),
    )
