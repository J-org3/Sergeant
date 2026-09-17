from dataclasses import dataclass, field


@dataclass
class ModelMessage:
    role: str
    content: str | None = None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None
    name: str | None = None


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str  # JSON string sin parsear, tal cual lo da el modelo


@dataclass
class ModelResponse:
    text: str
    provider: str
    model: str
    tool_calls: list[ToolCall] = field(default_factory=list)
