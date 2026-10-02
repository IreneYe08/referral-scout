#!/usr/bin/env python3
"""LinkedIn Unicode text formatter — Typegrow-equivalent styles. Stdlib only."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Callable

COMBINING_UNDERLINE = "\u0332"
COMBINING_STRIKETHROUGH = "\u0336"

# Mathematical italic 'h' is U+210E, not in the italic block.
ITALIC_H = "\u210e"

# Script / double-struck uppercase exceptions (Unicode spec).
SCRIPT_UPPER = {
    "B": "\u212c",
    "E": "\u2130",
    "F": "\u2131",
    "H": "\u210b",
    "I": "\u2110",
    "L": "\u2112",
    "M": "\u2133",
    "R": "\u211b",
}
DOUBLESTRUCK_UPPER = {
    "C": "\u2102",
    "H": "\u210d",
    "N": "\u2115",
    "P": "\u2119",
    "Q": "\u211a",
    "R": "\u211d",
    "Z": "\u2124",
}

STYLE_ALIASES = {
    "normal": "normal",
    "bold": "bold",
    "bold-sans": "bold-sans",
    "bold_sans": "bold-sans",
    "boldsans": "bold-sans",
    "italic": "italic",
    "italic-sans": "italic-sans",
    "italic_sans": "italic-sans",
    "italicsans": "italic-sans",
    "bold-italic": "bold-italic",
    "bold_italic": "bold-italic",
    "bolditalic": "bold-italic",
    "bold-italic-sans": "bold-italic-sans",
    "bold_italic_sans": "bold-italic-sans",
    "bolditalicsans": "bold-italic-sans",
    "sans": "sans",
    "monospace": "sans",
    "underline": "underline",
    "strikethrough": "strikethrough",
    "strike": "strikethrough",
    "bold-underline": "bold-underline",
    "bold_underline": "bold-underline",
    "bold-strikethrough": "bold-strikethrough",
    "bold_strikethrough": "bold-strikethrough",
    "script": "script",
    "doublestruck": "doublestruck",
    "double-struck": "doublestruck",
    "fullwidth": "fullwidth",
    "uppercase": "uppercase",
    "lowercase": "lowercase",
}

ALL_STYLES = [
    "normal",
    "bold",
    "bold-sans",
    "italic",
    "italic-sans",
    "bold-italic",
    "bold-italic-sans",
    "sans",
    "underline",
    "strikethrough",
    "bold-underline",
    "bold-strikethrough",
    "script",
    "doublestruck",
    "fullwidth",
    "uppercase",
    "lowercase",
]

LIST_TYPES = ("bullet", "numbered", "checklist", "ascending", "descending")
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
REVERSE_CIRCLED = "⓿❶❷❸❹❺❻❼❽❾❿"


def _map_range(
    text: str,
    upper_base: int,
    lower_base: int,
    upper_special: dict[str, str] | None = None,
    *,
    digit_base: int | None = None,
) -> str:
    out: list[str] = []
    for ch in text:
        if "A" <= ch <= "Z":
            if upper_special and ch in upper_special:
                out.append(upper_special[ch])
            else:
                out.append(chr(upper_base + ord(ch) - ord("A")))
        elif "a" <= ch <= "z":
            if ch == "h" and lower_base == 0x1D44E:  # mathematical italic
                out.append(ITALIC_H)
            else:
                out.append(chr(lower_base + ord(ch) - ord("a")))
        elif digit_base is not None and "0" <= ch <= "9":
            out.append(chr(digit_base + ord(ch) - ord("0")))
        else:
            out.append(ch)
    return "".join(out)


def _bold(text: str) -> str:
    return _map_range(text, 0x1D400, 0x1D41A, digit_base=0x1D7CE)


def _bold_sans(text: str) -> str:
    return _map_range(text, 0x1D5D4, 0x1D5EE, digit_base=0x1D7EC)


def _italic(text: str) -> str:
    # Serif italic has no digit glyphs; use sans-serif italic digits for consistency.
    return _map_range(text, 0x1D434, 0x1D44E, digit_base=0x1D7E2)


def _italic_sans(text: str) -> str:
    return _map_range(text, 0x1D608, 0x1D622, digit_base=0x1D7E2)


def _bold_italic(text: str) -> str:
    return _map_range(text, 0x1D468, 0x1D482)


def _bold_italic_sans(text: str) -> str:
    return _map_range(text, 0x1D63C, 0x1D656)


def _sans(text: str) -> str:
    return _map_range(text, 0x1D5A0, 0x1D5BA)


def _script(text: str) -> str:
    return _map_range(text, 0x1D49C, 0x1D4B6, SCRIPT_UPPER)


def _doublestruck(text: str) -> str:
    out: list[str] = []
    for ch in text:
        if "A" <= ch <= "Z":
            if ch in DOUBLESTRUCK_UPPER:
                out.append(DOUBLESTRUCK_UPPER[ch])
            else:
                out.append(chr(0x1D538 + ord(ch) - ord("A")))
        elif "a" <= ch <= "z":
            code = 0x1D552 + ord(ch) - ord("a")
            if code <= 0x1D56B:
                out.append(chr(code))
            else:
                out.append(ch)
        elif "0" <= ch <= "9":
            code = 0x1D7D8 + ord(ch) - ord("0")
            out.append(chr(code))
        else:
            out.append(ch)
    return "".join(out)


def _fullwidth(text: str) -> str:
    out: list[str] = []
    for ch in text:
        code = ord(ch)
        if code == 0x20:
            out.append("\u3000")
        elif 0x21 <= code <= 0x7E:
            out.append(chr(code - 0x21 + 0xFF01))
        else:
            out.append(ch)
    return "".join(out)


def _combining(text: str, mark: str) -> str:
    return "".join(ch + mark if ch not in "\n\r" else ch for ch in text)


STYLE_FN: dict[str, Callable[[str], str]] = {
    "normal": lambda t: t,
    "bold": _bold,
    "bold-sans": _bold_sans,
    "italic": _italic,
    "italic-sans": _italic_sans,
    "bold-italic": _bold_italic,
    "bold-italic-sans": _bold_italic_sans,
    "sans": _sans,
    "underline": lambda t: _combining(t, COMBINING_UNDERLINE),
    "strikethrough": lambda t: _combining(t, COMBINING_STRIKETHROUGH),
    "bold-underline": lambda t: _combining(_bold_sans(t), COMBINING_UNDERLINE),
    "bold-strikethrough": lambda t: _combining(_bold_sans(t), COMBINING_STRIKETHROUGH),
    "script": _script,
    "doublestruck": _doublestruck,
    "fullwidth": _fullwidth,
    "uppercase": str.upper,
    "lowercase": str.lower,
}


def linkedin_char_count(text: str) -> int:
    return sum(2 if ord(c) > 0xFFFF else 1 for c in text)


def apply_style(text: str, style: str) -> str:
    key = STYLE_ALIASES.get(style.lower(), style.lower())
    if key not in STYLE_FN:
        raise ValueError(f"Unknown style: {style}. Use --list-styles.")
    return STYLE_FN[key](text)


def apply_list(text: str, list_type: str) -> str:
    if list_type not in LIST_TYPES:
        raise ValueError(f"Unknown list type: {list_type}")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return text
    out: list[str] = []
    n = len(lines)
    for i, line in enumerate(lines):
        body = line.strip().lstrip("•").strip().lstrip("-").strip()
        if list_type == "bullet":
            out.append(f"• {body}")
        elif list_type == "numbered":
            out.append(f"{i + 1}. {body}")
        elif list_type == "checklist":
            out.append(f"☐ {body}")
        elif list_type == "ascending":
            marker = CIRCLED[i] if i < len(CIRCLED) else f"{i + 1}."
            out.append(f"{marker} {body}")
        elif list_type == "descending":
            idx = n - i - 1
            marker = REVERSE_CIRCLED[idx] if idx < len(REVERSE_CIRCLED) else f"{n - i}."
            out.append(f"{marker} {body}")
    return "\n".join(out)


INLINE_RE = re.compile(
    r"(\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|\*(.+?)\*|__(.+?)__|~~(.+?)~~)",
    re.DOTALL,
)


def apply_inline(text: str) -> str:
    """Parse **bold**, *italic*, ***bold-italic***, __underline__, ~~strike~~."""

    def repl(match: re.Match[str]) -> str:
        if match.group(2):
            return apply_style(match.group(2), "bold-italic-sans")
        if match.group(3):
            return apply_style(match.group(3), "bold-sans")
        if match.group(4):
            return apply_style(match.group(4), "italic-sans")
        if match.group(5):
            return apply_style(match.group(5), "underline")
        if match.group(6):
            return apply_style(match.group(6), "strikethrough")
        return match.group(0)

    return INLINE_RE.sub(repl, text)


def read_input(args: argparse.Namespace) -> str:
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            return f.read()
    if args.text is not None:
        return args.text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("Provide text as an argument, --file, or via stdin.")


def _ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            pass


def main() -> None:
    _ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="Format LinkedIn post text with Unicode styles.")
    parser.add_argument("text", nargs="?", help="Text to format")
    parser.add_argument("--file", "-f", help="Read text from file")
    parser.add_argument("--style", "-s", help="Apply one style to entire text")
    parser.add_argument("--list", dest="list_type", choices=LIST_TYPES, help="Convert lines to a list style")
    parser.add_argument("--inline", action="store_true", help="Parse **bold**, *italic*, __underline__, ~~strike~~")
    parser.add_argument("--smart", action="store_true", help="Smart layout: auto line breaks, bold, lists, hashtags")
    parser.add_argument("--explain", action="store_true", help="With --smart: print layout decisions to stderr")
    parser.add_argument("--show-all", action="store_true", help="Print all Typegrow-style variants")
    parser.add_argument("--list-styles", action="store_true", help="Print supported style names")
    parser.add_argument("--count", action="store_true", help="Show LinkedIn character count for output")
    args = parser.parse_args()

    if args.list_styles:
        for name in ALL_STYLES:
            print(name)
        for name in LIST_TYPES:
            print(f"list:{name}")
        print("smart")
        return

    raw = read_input(args)

    if args.smart:
        import json
        from smart_layout import smart_layout

        output, report = smart_layout(
            raw,
            promote_hook=True,
            less_bold=False,
        )
        print(output)
        if args.count:
            print(f"\n[LinkedIn chars: {linkedin_char_count(output)}]", file=sys.stderr)
        if args.explain:
            print(json.dumps({"actions": report.actions}, ensure_ascii=False, indent=2), file=sys.stderr)
        return

    if args.show_all:
        blocks: list[str] = []
        for style in ALL_STYLES:
            if style == "normal":
                continue
            formatted = apply_style(raw, style)
            blocks.append(f"## {style}\n{formatted}")
        for lt in LIST_TYPES:
            formatted = apply_list(raw, lt)
            blocks.append(f"## list:{lt}\n{formatted}")
        output = "\n\n".join(blocks)
    elif args.inline:
        output = apply_inline(raw)
    elif args.list_type:
        output = apply_list(raw, args.list_type)
    elif args.style:
        output = apply_style(raw, args.style)
    else:
        parser.error("Specify --style, --inline, --list, or --show-all")

    print(output)
    if args.count:
        print(f"\n[LinkedIn chars: {linkedin_char_count(output)}]", file=sys.stderr)


if __name__ == "__main__":
    main()
