#!/usr/bin/env python3
"""Лёгкая валидация Project Context System для Bakunity Infra."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REQUIRED_FILES = [
    "AGENTS.md",
    ".project/state.json",
    "docs/PROJECT_STATE.md",
    "docs/ACTIVE_WORK.md",
    "docs/ARCHITECTURE.md",
    "docs/ROADMAP.md",
    "docs/EVIDENCE.md",
    "docs/ADR/README.md",
    "docs/INCIDENTS/README.md",
]

REQUIRED_STATE_KEYS = {
    "schema_version",
    "project",
    "context_system",
    "state_based_on_commit",
    "last_reconciled_at",
    "phase",
    "implementation_status",
    "active_work",
    "authoritative",
}


def git_head(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).exists():
            errors.append(f"missing: {relative}")

    state_path = root / ".project/state.json"
    state: dict[str, object] = {}

    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"invalid .project/state.json: {exc}")

    if state:
        missing_keys = sorted(REQUIRED_STATE_KEYS - state.keys())
        for key in missing_keys:
            errors.append(f"state key missing: {key}")

        authoritative = state.get("authoritative")
        if not isinstance(authoritative, dict):
            errors.append("state.authoritative must be an object")
        else:
            for name, relative in authoritative.items():
                if not isinstance(relative, str):
                    errors.append(f"authoritative.{name} must be a path string")
                    continue
                if not (root / relative).exists():
                    errors.append(f"authoritative path missing: {name} -> {relative}")

        head = git_head(root)
        base = state.get("state_based_on_commit")
        if head and isinstance(base, str) and head != base:
            warnings.append(
                "Git HEAD differs from state_based_on_commit. Inspect drift and reconcile context "
                "if it changes project truth."
            )

    if errors:
        print("PCS context validation: FAIL")
        for item in errors:
            print(f"  ERROR: {item}")
        for item in warnings:
            print(f"  WARN: {item}")
        return 1

    print("PCS context validation: PASS")
    for item in warnings:
        print(f"  WARN: {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
