#!/usr/bin/env python3
"""Smart LinkedIn post layout: line breaks, bold/italic detection, lists, hashtags."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Same-directory import when run as script
sys.path.insert(0, str(Path(__file__).parent))
from format import apply_inline, linkedin_char_count  # noqa: E402
from hashtags import suggest_hashtags  # noqa: E402

try:
    from _util import ensure_utf8_stdout
except ImportError:
    def ensure_utf8_stdout() -> None:
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass

HASHTAG_RE = re.compile(r"(?<!\w)#([\w\u0080-\uFFFF]+)")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(\[]|\d)")
QUOTE_INLINE_RE = re.compile(r'(["\'""])(.+?)\1')
# Report titles, years, long titles: keep plain ASCII (cursor + search friendly).
QUOTE_SKIP_INNER_RE = re.compile(r"\b20\d{2}\b", re.I)
QUOTE_SKIP_AFTER_RE = re.compile(r"^\s*(report|article|study|paper|ebook|guide|whitepaper)\b", re.I)
STAT_RE = re.compile(
    r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?%|\d+(?:\.\d+)?x|\$[\d,]+(?:\.\d+)?|\d+\+\s*(?:users|customers|days|hours|weeks|months|years)?|\d+\s*(?:users|customers|days|hours|weeks|months|years))",
    re.I,
)
LIST_BULLET_RE = re.compile(r"^[-*•]\s+(.*)$")
LIST_NUMBER_RE = re.compile(r"^\d+[.)]\s+(.*)$")
LIST_CHECK_RE = re.compile(r"^\[[ xX]?\]\s+(.*)$|^[-*]\s+\[[ xX]?\]\s+(.*)$")
ARROW_OLD_NEW_RE = re.compile(r"^(.*?)\s*(?:→|->|-->|—>)\s*(.+)$")
THESIS_LINE_RE = re.compile(
    r"^The (remaining |biggest |main )?(challenge|opportunity|lesson|truth|problem|takeaway) is .+[.!]?$",
    re.I,
)
PUNCHY_HOOK_RE = re.compile(r"^[A-Z\"'(\[]")


@dataclass
class LayoutReport:
    actions: list[str] = field(default_factory=list)

    def log(self, msg: str) -> None:
        self.actions.append(msg)


def extract_hashtags(text: str, report: LayoutReport) -> tuple[str, list[str]]:
    tags: list[str] = []
    seen: set[str] = set()

    def repl(match: re.Match[str]) -> str:
        tag = match.group(1)
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            tags.append(f"#{tag}")
        return ""

    cleaned = HASHTAG_RE.sub(repl, text)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if tags:
        report.log(f"Moved {len(tags)} hashtag(s) to footer")
    return cleaned, tags


def is_list_line(line: str) -> tuple[str | None, str]:
    m = LIST_CHECK_RE.match(line)
    if m:
        body = m.group(1) or m.group(2) or ""
        return "checklist", body.strip()
    m = LIST_BULLET_RE.match(line)
    if m:
        return "bullet", m.group(1).strip()
    m = LIST_NUMBER_RE.match(line)
    if m:
        return "numbered", m.group(1).strip()
    return None, line


def is_hook_line(line: str, *, first: bool) -> bool:
    s = line.strip()
    if not s or s.startswith("#") or URL_RE.search(s) or '"' in s or "'" in s:
        return False
    if len(s) > 130:
        return False
    if not first:
        return False
    if s.endswith("?"):
        return True
    if len(s) <= 45:
        return True
    if len(s) <= 100 and not s.rstrip().endswith("."):
        return True
    return False


def is_section_header(line: str, *, after_hook: bool = False) -> bool:
    s = line.strip()
    if len(s) > 72 or len(s) < 3:
        return False
    if after_hook and not s.endswith(":"):
        return False
    if s.endswith(":") and s.count(".") == 0:
        return True
    if re.match(r"^(Step|Lesson|Tip|Part|Phase)\s+\d+\b", s, re.I):
        return True
    if re.match(r"^#{1,3}\s+\S", s):
        return True
    return False


def is_cta_line(line: str) -> bool:
    s = line.lower()
    cues = (
        "comment below",
        "dm me",
        "link in",
        "follow for",
        "repost if",
        "share if",
        "what do you think",
        "agree?",
        "let me know",
    )
    return any(c in s for c in cues)


def is_engagement_question(line: str) -> bool:
    s = line.strip()
    if not s.endswith("?"):
        return False
    lower = s.lower()
    cues = (
        "where do you",
        "what do you",
        "how do you",
        "who else",
        "anyone else",
        "you spend",
        "you seeing",
        "your experience",
        "thoughts on",
        "agree?",
    )
    return any(c in lower for c in cues)


def is_thesis_line(line: str) -> bool:
    s = line.strip().strip("*")
    if "**" in line or len(s) > 100 or len(s) < 20:
        return False
    return bool(THESIS_LINE_RE.match(s))


def is_punchy_hook(line: str) -> bool:
    s = line.strip()
    if len(s) < 8 or len(s) > 90 or not PUNCHY_HOOK_RE.match(s):
        return False
    if s.endswith("?"):
        return True
    if len(s) <= 45:
        return True
    return len(s) <= 85 and not s.endswith(".")


def promote_hook_lines(lines: list[str], report: LayoutReport) -> list[str]:
    """Move a short punchy line above a long opening context paragraph."""
    indices = [i for i, ln in enumerate(lines) if ln.strip()]
    if len(indices) < 2:
        return lines
    first_i = indices[0]
    first = lines[first_i].strip()
    if len(first) <= 55:
        return lines
    for j in indices[1:4]:
        candidate = lines[j].strip()
        if not is_punchy_hook(candidate):
            continue
        report.log(f"Promoted hook: {candidate[:55]}")
        rest = [ln for k, ln in enumerate(lines) if k != j]
        out: list[str] = []
        placed_hook = False
        for k, ln in enumerate(rest):
            if k == first_i and not placed_hook:
                out.append(candidate)
                out.append("")
                out.append(ln)
                placed_hook = True
            else:
                out.append(ln)
        return out
    return lines


def split_long_paragraph(text: str, max_chars: int = 220) -> list[str]:
    s = " ".join(text.split())
    if len(s) <= max_chars:
        return [s]
    parts = SENTENCE_SPLIT_RE.split(s)
    if len(parts) <= 1:
        return [s]
    chunks: list[str] = []
    buf = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        candidate = f"{buf} {part}".strip() if buf else part
        if len(candidate) <= max_chars:
            buf = candidate
        else:
            if buf:
                chunks.append(buf)
            buf = part
    if buf:
        chunks.append(buf)
    return chunks if chunks else [s]


def _should_skip_quote_italic(inner: str, text: str, match: re.Match[str]) -> bool:
    """Keep report/article titles in plain text — avoids digit breaks and editor cursor bugs."""
    if len(inner) > 35:
        return True
    if QUOTE_SKIP_INNER_RE.search(inner):
        return True
    after = text[match.end() : match.end() + 24]
    if QUOTE_SKIP_AFTER_RE.match(after):
        return True
    return False


def inject_inline_quotes(text: str, report: LayoutReport) -> str:
    count = 0
    skipped = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count, skipped
        inner = match.group(2)
        if len(inner) < 3 or len(inner) > 120:
            return match.group(0)
        if _should_skip_quote_italic(inner, text, match):
            skipped += 1
            return match.group(0)
        count += 1
        return f"*{inner}*"

    out = QUOTE_INLINE_RE.sub(repl, text)
    if count:
        report.log(f"Italicized {count} short quoted phrase(s)")
    if skipped:
        report.log(f"Kept {skipped} title/report quote(s) in plain text")
    return out


def inject_stat_bold(text: str, report: LayoutReport) -> str:
    if "**" in text:
        return text
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        val = match.group(1)
        if val.startswith("#"):
            return val
        count += 1
        return f"**{val}**"

    out = STAT_RE.sub(repl, text)
    if count:
        report.log(f"Bolded {count} stat/metric(s)")
    return out


def format_arrow_line(line: str, report: LayoutReport) -> str | None:
    m = ARROW_OLD_NEW_RE.match(line.strip())
    if not m:
        return None
    left, right = m.group(1).strip(), m.group(2).strip()
    if len(left) < 3 or len(right) < 3:
        return None
    report.log("Applied strikethrough → replacement on one line")
    return f"~~{left}~~ → {right}"


def bold_wrap(line: str) -> str:
    if line.startswith("**") and line.endswith("**"):
        return line
    return f"**{line}**"


def italic_wrap(line: str) -> str:
    if line.startswith("*") and line.endswith("*"):
        return line
    return f"*{line}*"


def process_blocks(
    lines: list[str],
    report: LayoutReport,
    *,
    less_bold: bool = False,
) -> list[str]:
    out: list[str] = []
    i = 0
    first_content = True
    bold_used = 0
    max_bold = 4
    hook_done = False

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line.startswith("**") and line.endswith("**"):
            out.append(line)
            report.log("Preserved manual bold line")
            bold_used += 1
            out.append("")
            i += 1
            first_content = False
            continue

        list_kind, body = is_list_line(line)
        if list_kind:
            items: list[str] = []
            while i < len(lines):
                lk, b = is_list_line(lines[i].strip())
                if not lk:
                    break
                items.append(b)
                i += 1
            prefix = {"bullet": "•", "numbered": None, "checklist": "☐"}[list_kind]
            report.log(f"Formatted {list_kind} list ({len(items)} items)")
            if list_kind == "numbered":
                formatted_items = []
                for item in items:
                    formatted_items.append(
                        inject_stat_bold(inject_inline_quotes(item, report), report)
                    )
                out.extend(f"{n}. {item}" for n, item in enumerate(formatted_items, 1))
            else:
                for item in items:
                    item = inject_stat_bold(inject_inline_quotes(item, report), report)
                    out.append(f"{prefix} {item}")
            out.append("")
            continue

        arrow = format_arrow_line(line, report)
        if arrow:
            out.append(apply_inline(arrow))
            out.append("")
            i += 1
            first_content = False
            continue

        if is_engagement_question(line):
            out.append(italic_wrap(inject_inline_quotes(line, report)))
            report.log("Italic engagement question")
            out.append("")
            i += 1
            first_content = False
            continue

        if is_cta_line(line):
            out.append(italic_wrap(inject_inline_quotes(line, report)))
            report.log("Italic CTA line")
            out.append("")
            i += 1
            first_content = False
            continue

        if is_hook_line(line, first=first_content) and bold_used < max_bold:
            out.append(bold_wrap(line))
            report.log("Bold hook (first line)")
            bold_used += 1
            out.append("")
            i += 1
            first_content = False
            hook_done = True
            continue

        if (
            not less_bold
            and is_section_header(line, after_hook=hook_done)
            and bold_used < max_bold
        ):
            hdr = line.rstrip(":")
            out.append(bold_wrap(hdr))
            report.log(f"Bold section header: {hdr[:40]}")
            bold_used += 1
            out.append("")
            i += 1
            first_content = False
            continue

        if is_thesis_line(line) and bold_used < max_bold:
            out.append(bold_wrap(line.strip().strip("*")))
            report.log("Bold thesis line")
            bold_used += 1
            out.append("")
            i += 1
            first_content = False
            continue

        para_lines: list[str] = []
        while i < len(lines) and lines[i].strip():
            lk, _ = is_list_line(lines[i].strip())
            if lk:
                break
            if is_section_header(lines[i].strip(), after_hook=hook_done) and para_lines:
                break
            para_lines.append(lines[i].strip())
            i += 1

        paragraph = " ".join(para_lines)
        chunks = split_long_paragraph(paragraph)
        if len(chunks) > 1:
            report.log("Split long paragraph at sentence boundaries")
        for chunk in chunks:
            chunk = inject_stat_bold(inject_inline_quotes(chunk, report), report)
            out.append(chunk)
        out.append("")
        first_content = False

    while out and out[-1] == "":
        out.pop()
    return out


def smart_layout(
    raw: str,
    *,
    aggressive_wrap: bool = True,
    auto_hashtags: bool = True,
    max_hashtags: int = 5,
    promote_hook: bool = True,
    less_bold: bool = False,
) -> tuple[str, LayoutReport]:
    report = LayoutReport()
    text = raw.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return "", report

    body, hashtags = extract_hashtags(text, report)

    if auto_hashtags:
        before = len(hashtags)
        hashtags = suggest_hashtags(text, hashtags, max_count=max_hashtags)
        added = len(hashtags) - before
        if added > 0:
            report.log(f"Added {added} suggested hashtag(s): {' '.join(hashtags[before:])}")
    lines = body.split("\n")

    if promote_hook:
        lines = promote_hook_lines(lines, report)

    if aggressive_wrap:
        normalized: list[str] = []
        for ln in lines:
            ln = ln.strip()
            if not ln:
                normalized.append("")
            elif len(ln) > 280 and not is_list_line(ln)[0] and not URL_RE.search(ln):
                normalized.extend(split_long_paragraph(ln))
                normalized.append("")
                report.log("Wrapped very long line")
            else:
                normalized.append(ln)
        lines = normalized

    markup_lines = process_blocks(lines, report, less_bold=less_bold)
    markup = "\n".join(markup_lines)

    if hashtags:
        markup = f"{markup}\n\n{' '.join(hashtags)}"

    formatted = apply_inline(markup)
    return formatted, report


def run_self_test() -> int:
    errors: list[str] = []

    out1, r1 = smart_layout(
        'See "Best AI Tools for Accountants 2026" report for details.',
        auto_hashtags=False,
    )
    if "𝘉" in out1 or "𝘐" in out1:
        errors.append("report title should stay plain ASCII")
    if not any("plain text" in a or "title/report" in a for a in r1.actions):
        errors.append("expected plain-text quote log")

    raw2 = (
        "As a PM at a startup I've been talking to accountants for months.\n"
        "One pattern appears repeatedly.\n"
    )
    out2, r2 = smart_layout(raw2, auto_hashtags=False)
    if not any("Promoted hook" in a for a in r2.actions):
        errors.append("expected hook promotion")
    if not out2.startswith("𝗢"):
        errors.append("hook should be first line bold")

    out3, _ = smart_layout("**The remaining challenge is workflow fragmentation.**", auto_hashtags=False)
    if "𝗧" not in out3:
        errors.append("manual bold line failed")

    out4, _ = smart_layout("Where do you spend the most time today?", auto_hashtags=False)
    if "𝘸" not in out4 and "𝘞" not in out4:
        errors.append("engagement question should be italic")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print("OK: all self-tests passed", file=sys.stderr)
    return 0


def main() -> None:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="Smart LinkedIn post layout and Unicode formatting.")
    parser.add_argument("text", nargs="?", help="Draft post text")
    parser.add_argument("--file", "-f", help="Read draft from file")
    parser.add_argument("--count", action="store_true", help="Print LinkedIn character count to stderr")
    parser.add_argument("--explain", action="store_true", help="Print layout decisions as JSON to stderr")
    parser.add_argument("--no-wrap", action="store_true", help="Skip aggressive long-line wrapping")
    parser.add_argument("--no-hashtags", action="store_true", help="Do not auto-suggest hashtags")
    parser.add_argument("--no-promote-hook", action="store_true", help="Keep original line order")
    parser.add_argument("--less-bold", action="store_true", help="Bold hook only — skip section headers")
    parser.add_argument(
        "--hashtags",
        type=int,
        default=5,
        metavar="N",
        help="Max hashtags in footer including any in draft (default: 5)",
    )
    parser.add_argument("--self-test", action="store_true", help="Run regression checks")
    args = parser.parse_args()

    if args.self_test:
        raise SystemExit(run_self_test())

    if args.file:
        raw = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        raw = args.text
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
    else:
        parser.error("Provide text, --file, or stdin.")

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
