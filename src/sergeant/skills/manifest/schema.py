from __future__ import annotations
from dataclasses import dataclass, field

VALID_PERMISSIONS = {"read_system", "shell", "gpio", "network", "filesystem"}
DANGEROUS_PERMISSIONS = {"shell", "gpio", "filesystem"}

REQUIRED_FIELDS = {"name", "version", "author", "entry_point", "permissions", "description"}


class ManifestValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


@dataclass
class SkillManifest:
    name: str
    version: str
    author: str
    entry_point: str
    permissions: list[str]
    description: str
    requires_confirmation: bool = False
    homepage: str | None = None
    checksum_sha256: str | None = None


def validate_manifest(data: dict) -> SkillManifest:
    errors: list[str] = []

    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        errors.append(f"Campos obligatorios ausentes: {sorted(missing)}")

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("'name' debe ser un string no vacío")

    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append("'version' debe ser un string no vacío")

    entry_point = data.get("entry_point")
    if not isinstance(entry_point, str) or "." not in entry_point:
        errors.append("'entry_point' debe ser un string tipo 'modulo.submodulo'")

    permissions = data.get("permissions")
    if not isinstance(permissions, list) or not all(isinstance(p, str) for p in permissions):
        errors.append("'permissions' debe ser una lista de strings")
        permissions = []

    unknown_perms = set(permissions) - VALID_PERMISSIONS
    if unknown_perms:
        errors.append(f"Permisos desconocidos: {sorted(unknown_perms)}. Válidos: {sorted(VALID_PERMISSIONS)}")

    requires_confirmation = data.get("requires_confirmation", False)
    if not isinstance(requires_confirmation, bool):
        errors.append("'requires_confirmation' debe ser booleano")

    dangerous_requested = set(permissions) & DANGEROUS_PERMISSIONS
    if dangerous_requested and not requires_confirmation:
        errors.append(
            f"La skill solicita permisos sensibles {sorted(dangerous_requested)} "
            "pero 'requires_confirmation' no está en true. Rechazada por seguridad."
        )

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("'description' debe ser un string no vacío")

    if errors:
        raise ManifestValidationError(errors)

    return SkillManifest(
        name=name,
        version=version,
        author=data.get("author", "desconocido"),
        entry_point=entry_point,
        permissions=permissions,
        description=description,
        requires_confirmation=requires_confirmation,
        homepage=data.get("homepage"),
        checksum_sha256=data.get("checksum_sha256"),
    )
