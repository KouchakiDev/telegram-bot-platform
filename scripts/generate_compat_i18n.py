from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "telegram_bot_platform" / "compat"
OUT = ROOT / "resources" / "i18n" / "compat_catalog.json"
USER_CALLS = {"send_message", "reply_to", "send_photo", "send_video", "send_document", "send_audio", "send_voice", "send_animation", "edit_message_text", "edit_message_caption", "answer_callback_query"}
BUTTONS = {"InlineKeyboardButton", "KeyboardButton"}
DICT_NAMES = {"BUTTONS", "MESSAGES", "AUTH_MESSAGES", "AUTH_PROMPTS", "IDENTITY_VERIFICATION_PROMPTS", "STATUS_INFO", "STATUS_TITLES", "REQUEST_TYPE_NAMES", "TEMPLATES", "DYNAMIC_NOTIFICATION_CONFIG", "DEFAULT_REASONS", "SERVICES"}

def stable_key(text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]
    return f"legacy.text.{digest}"

def source_text(node: ast.AST) -> tuple[str, str] | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value, "literal"
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        index = 0
        for part in node.values:
            if isinstance(part, ast.Constant):
                parts.append(str(part.value))
            else:
                parts.append(f"{{value_{index}}}")
                index += 1
        return "".join(parts), "template"
    return None

def add(found: dict[str, dict[str, object]], value: str, kind: str, path: Path, line: int) -> None:
    if not value.strip():
        return
    if len(value) < 2:
        return
    key = stable_key(value)
    found.setdefault(key, {"key": key, "source": value, "en": value, "fa": value, "kind": kind, "sources": []})
    found[key]["sources"].append(f"{path.relative_to(ROOT)}:{line}")

def walk_file(path: Path) -> list[ast.AST]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return []
    nodes: list[ast.AST] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func.attr if isinstance(node.func, ast.Attribute) else (node.func.id if isinstance(node.func, ast.Name) else "")
            if fn in USER_CALLS or fn in BUTTONS:
                for arg in node.args:
                    candidate = source_text(arg)
                    if candidate:
                        nodes.append((candidate[0], candidate[1], arg.lineno))
                for kw in node.keywords:
                    if kw.arg in {"text", "caption"}:
                        candidate = source_text(kw.value)
                        if candidate:
                            nodes.append((candidate[0], candidate[1], kw.value.lineno))
        if isinstance(node, ast.Assign):
            names = {target.id for target in node.targets if isinstance(target, ast.Name)}
            if names & DICT_NAMES:
                for value_node in ast.walk(node.value):
                    candidate = source_text(value_node)
                    if candidate:
                        nodes.append((candidate[0], candidate[1] + ":config", value_node.lineno))
    return nodes

def main() -> None:
    found: dict[str, dict[str, object]] = {}
    for path in sorted(SRC.rglob("*.py")):
        for value, kind, line in walk_file(path):
            if "\\n" not in value and "\n" not in value and value.strip().startswith(("SELECT ", "UPDATE ", "INSERT ", "DELETE ", "ALTER ", "CREATE ", "DROP ")):
                continue
            add(found, value, kind, path, line)
    rows = sorted(found.values(), key=lambda x: str(x["key"]))
    for row in rows:
        row["sources"] = row["sources"][:8]
    OUT.write_text(json.dumps({"items": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(rows)} compatibility localization keys: {OUT}")

if __name__ == "__main__":
    main()
