#!/usr/bin/env python3
"""Apply safe, repository-local GitHub PCS conveniences via the GitHub CLI.

V1 intentionally automates labels only. Project and ruleset manifests are kept
as reviewed policy/spec files because applying governance can affect repository
access and merge behavior.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure safe GitHub PCS conveniences")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--repo", help="owner/name; otherwise gh resolves the current repository")
    parser.add_argument("--apply-labels", action="store_true", help="Create/update recommended PCS labels")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    if shutil.which("gh") is None:
        print("GitHub CLI 'gh' is required for setup_github.py", file=sys.stderr)
        return 2

    auth = run(["gh", "auth", "status"], root)
    if auth.returncode != 0:
        print(auth.stderr or auth.stdout, file=sys.stderr)
        return 2

    repo = args.repo
    if not repo:
        resolved = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], root)
        if resolved.returncode != 0 or not resolved.stdout.strip():
            print(resolved.stderr or "Could not resolve GitHub repository", file=sys.stderr)
            return 2
        repo = resolved.stdout.strip()

    print(f"PCS GitHub target: {repo}")

    if args.apply_labels:
        path = root / ".project/github/labels.json"
        labels = json.loads(path.read_text(encoding="utf-8"))
        for label in labels:
            result = run([
                "gh", "label", "create", label["name"], "--repo", repo,
                "--color", label["color"], "--description", label["description"], "--force"
            ], root)
            if result.returncode != 0:
                print(result.stderr or result.stdout, file=sys.stderr)
                return result.returncode
        print(f"Applied {len(labels)} PCS labels")
    else:
        print("No mutations requested. Use --apply-labels to apply the safe label manifest.")

    print("Project model: .project/github/project-model.json")
    print("Ruleset policy: .project/github/ruleset-policy.json")
    print("Review governance before applying Project/Ruleset changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
