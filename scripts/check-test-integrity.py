#!/usr/bin/env python3
"""Detect changes that weaken the test suite in a pull request.

AI coding agents sometimes make a failing test pass by deleting it, skipping
it, or removing assertions instead of fixing the code. This script compares
the base and head revisions of tests/ and reports:

  - deleted test files
  - deleted test functions
  - newly added skip / xfail markers
  - a drop in the total number of assert statements

Usage: check-test-integrity.py <base-ref> <head-ref>
Exit code 1 when any weakening is found, 0 otherwise.
"""

import ast
import subprocess
import sys

TEST_DIR = "tests/"
SKIP_MARKERS = ("skip", "skipif", "xfail")


def git(*args):
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout


def test_files(ref):
    out = git("ls-tree", "-r", "--name-only", ref, "--", TEST_DIR)
    return {p for p in out.splitlines() if p.endswith(".py")}


def read(ref, path):
    return git("show", f"{ref}:{path}")


def summarize(source):
    """Return (test function names, skip marker count, assert count)."""
    tree = ast.parse(source)
    names, skips, asserts = set(), 0, 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test"):
                names.add(node.name)
        elif isinstance(node, ast.Assert):
            asserts += 1
        elif isinstance(node, ast.Attribute) and node.attr in SKIP_MARKERS:
            skips += 1
    return names, skips, asserts


def main(base, head):
    base_files, head_files = test_files(base), test_files(head)
    problems = []

    for path in sorted(base_files - head_files):
        problems.append(f"deleted test file: {path}")

    base_asserts = head_asserts = 0
    for path in sorted(base_files | head_files):
        b = summarize(read(base, path)) if path in base_files else (set(), 0, 0)
        h = summarize(read(head, path)) if path in head_files else (set(), 0, 0)
        base_asserts += b[2]
        head_asserts += h[2]
        if path in head_files:
            for name in sorted(b[0] - h[0]):
                problems.append(f"deleted test function: {path}::{name}")
            if h[1] > b[1]:
                problems.append(f"added skip/xfail marker(s): {path} (+{h[1] - b[1]})")

    if head_asserts < base_asserts:
        problems.append(f"assert count dropped: {base_asserts} -> {head_asserts}")

    if problems:
        print("Test suite weakened:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"No weakening found (asserts: {base_asserts} -> {head_asserts}).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
