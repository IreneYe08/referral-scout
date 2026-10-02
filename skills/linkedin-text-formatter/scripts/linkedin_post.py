#!/usr/bin/env python3
"""Single entry point: smart LinkedIn post layout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _util import ensure_utf8_stdout, skill_scripts_dir, write_temp_draft

sys.path.insert(0, str(skill_scripts_dir()))
from format import linkedin_char_count  # noqa: E402
from smart_layout import smart_layout  # noqa: E402


def main() -> None:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="Format a LinkedIn post (smart layout + Unicode).")
    parser.add_argument("text", nargs="?", help="Draft text")
    parser.add_argument("--file", "-f", type=Path, help="Read draft from file")
    parser.add_argument("--stdin", action="store_true", help="Read draft from stdin")
    parser.add_argument("--count", action="store_true", help="LinkedIn char count → stderr")
    parser.add_argument("--explain", action="store_true", help="Layout decisions JSON → stderr")
    parser.add_argument("--no-wrap", action="store_true")
    parser.add_argument("--no-hashtags", action="store_true")
    parser.add_argument("--no-promote-hook", action="store_true", help="Keep original line order")
    parser.add_argument("--less-bold", action="store_true", help="Bold hook only, no section headers")
    parser.add_argument("--hashtags", type=int, default=5, metavar="N")
    parser.add_argument("--self-test", action="store_true", help="Run regression checks")
    args = parser.parse_args()

    if args.self_test:
        from smart_layout import run_self_test

        raise SystemExit(run_self_test())

    if args.file:
        raw = args.file.read_text(encoding="utf-8")
    elif args.stdin or not sys.stdin.isatty():
        raw = sys.stdin.read()
    elif args.text:
        raw = args.text
    else:
        parser.error("Provide text, --file, --stdin, or pipe on stdin.")

    output, report = smart_layout(
        raw,
        aggressive_wrap=not args.no_wrap,
        auto_hashtags=not args.no_hashtags,
        max_hashtags=max(0, args.hashtags),
        promote_hook=not args.no_promote_hook,
        less_bold=args.less_bold,
    )
    print(output)
    if args.count:
        print(f"[LinkedIn chars: {linkedin_char_count(output)}]", file=sys.stderr)
    if args.explain:
        print(json.dumps({"actions": report.actions}, ensure_ascii=False, indent=2), file=sys.stderr)


if __name__ == "__main__":
    main()
