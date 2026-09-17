from __future__ import annotations
import importlib
import inspect
import pkgutil
import logging

from .base import SkillDefinition

logger = logging.getLogger(__name__)


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, SkillDefinition] = {}

    def register(self, definition: SkillDefinition) -> None:
        if definition.name in self._skills:
            logger.warning("Skill '%s' ya registrada, sobrescribiendo", definition.name)
        self._skills[definition.name] = definition

    def get(self, name: str) -> SkillDefinition | None:
        return self._skills.get(name)

    def all(self) -> list[SkillDefinition]:
        return list(self._skills.values())

    def to_openai_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": s.name,
                    "description": s.description,
                    "parameters": s.parameters_schema,
                },
            }
            for s in self._skills.values()
        ]

    def autodiscover(self, package_name: str = "Sergeant.skills") -> None:
        package = importlib.import_module(package_name)
        for _, module_name, is_pkg in pkgutil.walk_packages(
            package.__path__, prefix=f"{package_name}."
        ):
            if is_pkg:
                continue
            module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                definition = getattr(attr, "_skill_definition", None)
                if definition is not None:
                    self.register(definition)
        logger.info("Skills registradas: %s", [s.name for s in self.all()])

    @staticmethod
    def is_async(func) -> bool:
        return inspect.iscoroutinefunction(func)


skill_registry = SkillRegistry()
