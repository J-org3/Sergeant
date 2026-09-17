import uuid
import httpx

from sergeant.config import Settings
from sergeant.models.base import ModelMessage, ModelResponse, ToolCall


class OllamaProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate(
        self,
        messages: list[ModelMessage],
        tools: list[dict] | None = None,
    ) -> ModelResponse:
        payload = {
            "model": self.settings.ollama_model,
            "messages": [_message_to_payload(message) for message in messages],
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                f"{self.settings.ollama_base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        message_data = data.get("message", {})
        text = message_data.get("content", "")

        tool_calls: list[ToolCall] = []
        for tc in message_data.get("tool_calls", []) or []:
            function = tc.get("function", {})
            tool_calls.append(
                ToolCall(
                    id=tc.get("id") or f"call_{uuid.uuid4().hex[:12]}",
                    name=function.get("name", ""),
                    arguments=_arguments_to_str(function.get("arguments", {})),
                )
            )

        return ModelResponse(
            text=text.strip(),
            provider="ollama",
            model=self.settings.ollama_model,
            tool_calls=tool_calls,
        )


def _message_to_payload(message: ModelMessage) -> dict:
    payload: dict = {"role": message.role}
    if message.content is not None:
        payload["content"] = message.content
    if message.tool_calls is not None:
        payload["tool_calls"] = message.tool_calls
    if message.tool_call_id is not None:
        payload["tool_call_id"] = message.tool_call_id
    if message.name is not None:
        payload["name"] = message.name
    return payload


def _arguments_to_str(arguments) -> str:
    import json
    if isinstance(arguments, str):
        return arguments
    return json.dumps(arguments, ensure_ascii=False)
