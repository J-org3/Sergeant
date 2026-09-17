"""Uso: python3 -m Sergeant.skills.adapter.inspect_cli ruta/al/SKILL.md
Solo LEE y muestra metadata. No ejecuta nada, no instala nada."""
from __future__ import annotations
import sys
from sergeant.skills.adapter.parser import parse_skill_md


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python3 -m Sergeant.skills.adapter.inspect_cli <ruta_SKILL.md>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        content = f.read()

    meta = parse_skill_md(content)

    print(f"name: {meta.name}")
    print(f"description: {meta.description[:200]}")
    print(f"triggers: {meta.triggers}")
    print(f"declared_permissions: {meta.declared_permissions}")
    print(f"has_embedded_scripts: {meta.has_embedded_scripts}")
    print(f"script_languages: {meta.script_languages}")

    if meta.has_embedded_scripts:
        print()
        print("⚠️  ESTA SKILL TRAE CÓDIGO EMBEBIDO.")
        print("    No se ejecuta automáticamente. Revisa manualmente antes de integrarla:")
        print(f"    python3 -m Sergeant.skills.adapter.inspect_cli {path} --show-code")

    if "--show-code" in sys.argv:
        import re
        blocks = re.findall(r"```(\w+)?\n(.*?)```", meta.body, re.DOTALL)
        for i, (lang, code) in enumerate(blocks, 1):
            print(f"\n--- bloque de código {i} ({lang or 'sin lenguaje'}) ---")
            print(code.strip())


if __name__ == "__main__":
    main()
