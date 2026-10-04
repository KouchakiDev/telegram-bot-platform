from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "logic_parity_manifest.json"

# Names/constants/import metadata can legitimately change during globalization and
# packaging. Control-flow and statement nodes inside function bodies are the useful
# invariant for detecting accidental logic deletion during decomposition.
IGNORED_BODY_NODES = {
    "Name",
    "Attribute",
    "Constant",
    "Load",
    "Store",
    "Del",
    "alias",
    "arg",
    "keyword",
    "comprehension",
    "withitem",
    "operator",
    "boolop",
    "unaryop",
    "cmpop",
    "expr_context",
}


def count_tree(path: Path) -> tuple[int, int, int, int, int, dict[str, int]]:
    source = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source)
    functions = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
    classes = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
    decorated_functions = sum(
        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and bool(n.decorator_list)
        for n in ast.walk(tree)
    )
    decorator_entries = sum(
        len(n.decorator_list)
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    body_nodes: Counter[str] = Counter()
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for statement in fn.body:
                for node in ast.walk(statement):
                    node_type = type(node).__name__
                    if node_type not in IGNORED_BODY_NODES:
                        body_nodes[node_type] += 1
    return (
        len(source.splitlines()),
        classes,
        functions,
        decorated_functions,
        decorator_entries,
        dict(body_nodes),
    )


def verify() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[dict[str, Any]] = []
    totals = Counter()

    for row in manifest:
        totals["sources"] += 1
        expected = {
            key: int(row[key])
            for key in (
                "source_lines",
                "destination_lines",
                "source_classes",
                "destination_classes",
                "source_functions",
                "destination_functions",
                "source_decorated_functions",
                "destination_decorated_functions",
                "source_decorator_entries",
                "destination_decorator_entries",
            )
        }
        for key, value in expected.items():
            totals[key] += value

        actual_stats = [count_tree(ROOT / destination) for destination in row["destinations"]]
        aggregate = tuple(sum(stats[index] for stats in actual_stats) for index in range(5))
        actual_body_nodes: Counter[str] = Counter()
        for stats in actual_stats:
            actual_body_nodes.update(stats[5])

        expected_body_nodes: dict[str, int] = row.get("source_function_body_nodes", {})
        body_failures = {
            node_type: (int(expected_count), int(actual_body_nodes.get(node_type, 0)))
            for node_type, expected_count in expected_body_nodes.items()
            if actual_body_nodes.get(node_type, 0) < int(expected_count)
        }

        checks = {
            "classes": aggregate[1] >= int(row["source_classes"]),
            "functions": aggregate[2] >= int(row["source_functions"]),
            "decorated_functions": aggregate[3] >= int(row["source_decorated_functions"]),
            "decorator_entries": aggregate[4] >= int(row["source_decorator_entries"]),
            "function_body_nodes": not body_failures,
        }
        if not all(checks.values()):
            failures.append(
                {
                    "source_id": row.get("source_id", "unknown"),
                    "expected": expected,
                    "actual": aggregate,
                    "body_node_failures": body_failures,
                    "checks": checks,
                }
            )

    return {
        "ok": not failures,
        "failures": failures,
        "totals": dict(totals),
    }


def main() -> int:
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
