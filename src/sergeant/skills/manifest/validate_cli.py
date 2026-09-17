"""Uso: python3 -m Sergeant.skills.manifest.validate_cli ruta/al/manifest.json"""
from __future__ import annotations
import json
import sys
from sergeant.skills.manifest.schema import validate_manifest, ManifestValidationError


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python3 -m Sergeant.skills.manifest.validate_cli <ruta_manifest.json>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR leyendo el manifest: {exc}")
        sys.exit(1)

    try:
        manifest = validate_manifest(data)
    except ManifestValidationError as exc:
        print("❌ Manifest RECHAZADO:")
        for err in exc.errors:
            print(f"  - {err}")
        sys.exit(1)

    print("✅ Manifest válido:")
    print(f"  name: {manifest.name}")
    print(f"  version: {manifest.version}")
    print(f"  author: {manifest.author}")
    print(f"  permissions: {manifest.permissions}")
    print(f"  requires_confirmation: {manifest.requires_confirmation}")


if __name__ == "__main__":
    main()
