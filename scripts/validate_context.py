#!/usr/bin/env python3
"""Validate the structural and readiness contract of a PCS installation."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REQUIRED_CORE = [
    "AGENTS.md",
    ".project/state.json",
    "docs/PROJECT_STATE.md",
    "docs/ARCHITECTURE.md",
    "docs/ROADMAP.md",
    "docs/ADR/README.md",
]

REQUIRED_STATE_KEYS = {
    "schema_version",
    "project",
    "state_doc",
    "architecture_doc",
    "roadmap_doc",
    "adr_dir",
    "state_based_on_commit",
    "status",
    "updated_at",
}

POINTER_KEYS = {
    "state_doc",
    "active_work_doc",
    "architecture_doc",
    "roadmap_doc",
    "adr_dir",
    "incidents_dir",
    "evidence_doc",
}

BOOTSTRAP_STATUSES = {"", "bootstrap", "unknown", "template"}

BOOTSTRAP_MARKERS = {
    "docs/PROJECT_STATE.md": [
        "Describe in 2–5 sentences what this project exists to do.",
        "Add only facts that are true now.",
        "Describe completed capabilities that matter to the current project state.",
        "Current meaningful work, if any.",
        "Known current limitations.",
        "Invariants or boundaries that future agents must preserve.",
    ],
    "docs/ARCHITECTURE.md": [
        "Describe the system and its boundaries.",
        "Replace this diagram with the real architecture.",
        "Describe the critical data/control flows.",
        "Describe runtime topology if relevant.",
    ],
    "docs/ROADMAP.md": [
        "Current product/engineering milestone.",
        "Next meaningful milestone(s).",
        "Future direction that is useful but not active work.",
    ],
    "docs/ACTIVE_WORK.md": [
        "What are we doing right now?",
        "PR: none / number",
        "What is already accepted and must not be casually reopened?",
        "None / describe blocker.",
        "Single safest next action.",
        "List expensive/live scenarios that should not be repeated without a regression reason.",
        "What actions require explicit approval?",
    ],
}

TEMPLATE_PATTERN = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def git(root: Path, *args: str) -> tuple[int, str]:
    try:
        p = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return 127, "git not found"
    return p.returncode, (p.stdout or p.stderr).strip()


def readiness_errors(root: Path, state: dict) -> list[str]:
    errors: list[str] = []

    status = str(state.get("status", "")).strip().lower()
    if status in BOOTSTRAP_STATUSES:
        errors.append(
            "state.json status is still bootstrap/unknown; set a real project lifecycle status after initial context is populated"
        )

    files_to_scan = set(REQUIRED_CORE)
    active_work = state.get("active_work_doc")
    if active_work:
        files_to_scan.add(str(active_work))

    for rel in sorted(files_to_scan):
        path = root / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        if TEMPLATE_PATTERN.search(text):
            errors.append(f"unresolved template placeholder in ready context: {rel}")

        for marker in BOOTSTRAP_MARKERS.get(rel, []):
            if marker in text:
                errors.append(f"bootstrap prompt still present in {rel}: {marker}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument(
        "--ready",
        action="store_true",
        help="Require populated project context, not just structurally installed PCS files",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_CORE:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    state_path = root / ".project/state.json"
    state: dict = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid .project/state.json: {exc}")

    if state:
        missing = sorted(REQUIRED_STATE_KEYS - set(state))
        for key in missing:
            errors.append(f"state.json missing key: {key}")

        if state.get("schema_version") != 1:
            errors.append("unsupported schema_version; expected 1")

        for key in POINTER_KEYS:
            value = state.get(key)
            if not value:
                continue
            if not (root / value).exists():
                errors.append(f"state pointer {key} does not exist: {value}")

        base = state.get("state_based_on_commit")
        if base:
            code, _ = git(root, "rev-parse", "--git-dir")
            if code == 0:
                code, _ = git(root, "cat-file", "-e", f"{base}^{{commit}}")
                if code != 0:
                    warnings.append(
                        "state_based_on_commit is not present in local Git history; "
                        "this can be normal immediately after installation before first context commit"
                    )
                else:
                    code, _ = git(root, "merge-base", "--is-ancestor", base, "HEAD")
                    if code != 0:
                        errors.append("state_based_on_commit is not an ancestor of HEAD")
                    else:
                        code, head = git(root, "rev-parse", "HEAD")
                        if code == 0 and not head.startswith(str(base)):
                            warnings.append(
                                "HEAD differs from state_based_on_commit; inspect relevant diff for context drift"
                            )

    if args.ready and state:
        errors.extend(readiness_errors(root, state))

    mode = "readiness" if args.ready else "structural"

    if errors:
        print(f"PCS {mode} validation: FAIL")
        for item in errors:
            print(f"ERROR: {item}")
        for item in warnings:
            print(f"WARN: {item}")
        return 1

    print(f"PCS {mode} validation: PASS")
    for item in warnings:
        print(f"WARN: {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
