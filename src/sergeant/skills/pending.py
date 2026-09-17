from __future__ import annotations
from dataclasses import dataclass, field
from sergeant.models.base import ModelMessage


@dataclass
class PendingConfirmation:
    chat_id: int
    tool_name: str
    tool_args: dict
    tool_call_id: str
    provider_name: str  # "azure" u "ollama", para saber con qué proveedor seguir el loop
    conversation: list[ModelMessage] = field(default_factory=list)


class PendingConfirmationStore:
    """Guarda como máximo una confirmación pendiente por chat_id.
    En memoria: válido para un agente de un solo usuario en una Raspberry Pi."""

    def __init__(self) -> None:
        self._pending: dict[int, PendingConfirmation] = {}

    def set(self, confirmation: PendingConfirmation) -> None:
        self._pending[confirmation.chat_id] = confirmation

    def get(self, chat_id: int) -> PendingConfirmation | None:
        return self._pending.get(chat_id)

    def clear(self, chat_id: int) -> None:
        self._pending.pop(chat_id, None)


pending_store = PendingConfirmationStore()
