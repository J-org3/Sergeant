import logging
from openai import AsyncAzureOpenAI
from sergeant.config import Settings
from sergeant.models.base import ModelMessage, ModelResponse, ToolCall

logger = logging.getLogger(__name__)


class AzureOpenAIProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
        )

    async def generate(
        self,
        messages: list[ModelMessage],
        tools: list[dict] | None = None,
    ) -> ModelResponse:
        payload = [_message_to_payload(message) for message in messages]

        kwargs = {
            "model": self.settings.azure_openai_deployment,
            "messages": payload,
            "max_completion_tokens": 1200,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = await self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message

        tool_calls: list[ToolCall] = []
        if message.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=tc.function.arguments or "{}",
                )
                for tc in message.tool_calls
            ]

        text = message.content or ""
        return ModelResponse(
            text=text.strip(),
            provider="azure",
            model=self.settings.azure_openai_deployment,
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
