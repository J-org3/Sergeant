from __future__ import annotations
import re
from dataclasses import dataclass, field

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class ClawHubSkillMeta:
    """Metadata extraída de un SKILL.md de ClawHub.
    Solo lectura de texto -- no ejecuta nada."""
    name: str
    description: str
    triggers: list[str] = field(default_factory=list)
    raw_frontmatter: dict = field(default_factory=dict)
    body: str = ""
    declared_permissions: list[str] = field(default_factory=list)
    has_embedded_scripts: bool = False
    script_languages: list[str] = field(default_factory=list)


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
CODE_BLOCK_RE = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)


def parse_skill_md(content: str) -> ClawHubSkillMeta:
    if yaml is None:
        raise RuntimeError("Falta PyYAML. Instala con: pip install pyyaml")

    match = FRONTMATTER_RE.match(content)
    if not match:
        raise ValueError("SKILL.md sin frontmatter YAML válido (---...---)")

    frontmatter_raw, body = match.groups()
    frontmatter = yaml.safe_load(frontmatter_raw) or {}

    code_blocks = CODE_BLOCK_RE.findall(body)
    languages = sorted({lang.lower() for lang, _ in code_blocks if lang})

    name = frontmatter.get("name") or frontmatter.get("id") or "skill_sin_nombre"
    description = frontmatter.get("description", "").strip()
    triggers = frontmatter.get("triggers", [])
    if isinstance(triggers, str):
        triggers = [triggers]

    permissions = frontmatter.get("permissions", [])
    if isinstance(permissions, str):
        permissions = [permissions]

    return ClawHubSkillMeta(
        name=name,
        description=description,
        triggers=triggers,
        raw_frontmatter=frontmatter,
        body=body.strip(),
        declared_permissions=permissions,
        has_embedded_scripts=bool(code_blocks),
        script_languages=languages,
    )
