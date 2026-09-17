from __future__ import annotations
import inspect
from dataclasses import dataclass
from typing import Any, Callable, get_type_hints

@dataclass
class SkillDefinition:
    name: str
    description: str
    func: Callable[..., Any]
    parameters_schema: dict
    requires_confirmation: bool = False
    category: str = "general"

_PYTHON_TO_JSON_TYPE = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}

def skill(
    name: str | None = None,
    description: str = "",
    requires_confirmation: bool = False,
    category: str = "general",
):
    """Decorador que convierte una función Python en una skill invocable
    por el modelo, generando automáticamente el JSON schema de parámetros."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)
        hints = get_type_hints(func)

        properties: dict[str, Any] = {}
        required: list[str] = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            py_type = hints.get(param_name, str)
            json_type = _PYTHON_TO_JSON_TYPE.get(py_type, "string")
            properties[param_name] = {"type": json_type}
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        schema = {
            "type": "object",
            "properties": properties,
            "required": required,
        }

        func._skill_definition = SkillDefinition(
            name=name or func.__name__,
            description=description or (func.__doc__ or "").strip(),
            func=func,
            parameters_schema=schema,
            requires_confirmation=requires_confirmation,
            category=category,
        )
        return func

    return decorator
