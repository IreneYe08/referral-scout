---
name: linkedin-text-formatter
description: >-
  LinkedIn post formatter: 8-block post structure, anti-AI voice
  rules, smart Unicode layout (hook, thesis, lists, hashtags), emoji guidance.
  Use when writing or formatting LinkedIn posts, GTM copy, PM thought leadership,
  paste-ready LinkedIn content, or social posts with your agent. Triggers: LinkedIn
  post, format LinkedIn, LinkedIn formatter, smart排版, Typegrow, paste-ready post.
---

# LinkedIn Text Formatter

Self-contained skill: scripts live in `scripts/` next to this file. **Always run the CLI** — never hand-type Unicode bold/italic.

## Install

```powershell
git clone https://github.com/IreneYe08/linkedin-text-formatter-cortex.git <skills-dir>\linkedin-text-formatter
```

macOS / Linux:

```bash
git clone https://github.com/IreneYe08/linkedin-text-formatter-cortex.git <skills-dir>/linkedin-text-formatter
```

Verify: `python <skills-dir>/linkedin-text-formatter/scripts/linkedin_post.py --self-test` (Windows: `py -3 ...`)

Dedicated repo: [https://github.com/IreneYe08/linkedin-text-formatter-cortex](https://github.com/IreneYe08/linkedin-text-formatter-cortex)

## Agent workflow

1. User gives rough draft, brief, or asks to write a LinkedIn post
2. If drafting from scratch → read [linkedin-post-guideline.md](linkedin-post-guideline.md) + [Anti-AI_Writing_Guidelines.md](Anti-AI_Writing_Guidelines.md) first
3. Save draft to temp file (Windows: `%TEMP%\draft.txt`)
4. Run formatter from **this skill directory**:

```bash
python scripts/linkedin_post.py --file draft.txt --count --explain
```

Windows: `py -3 scripts/linkedin_post.py --file %TEMP%\draft.txt --count --explain`

5. Return paste-ready output in a plain code fence + brief `--explain` summary + char count if >2500

**Never hand-convert Unicode.** Use `--less-bold` if user wants minimal emphasis.

## Use cases

| Scenario | What to do |
|----------|------------|
| PM / GTM thought leadership | 8-block structure → smart layout |
| Research report promo | Plain `"Report Title 2026"` — no Unicode italic on titles |
| Notes → mobile post | Auto spacing, hook promotion, bullets |
| Polish existing draft | Run CLI on user's text as-is |

## Smart layout (automatic via CLI)

| Signal | Action |
|--------|--------|
| Long opener + punchy line 2 | Promote hook to top |
| Hook line | Full-line Unicode bold |
| `The challenge is …` | Bold thesis |
| Lists `-` / `1.` | Bullet / numbered |
| Closing `where do you…?` | Italic engagement question |
| Report `"Title 2026" report` | Plain ASCII quotes |
| Body keywords | Auto hashtags (footer, max 5) |

Details: [layout-rules.md](layout-rules.md)

## Unicode visual rules (editorial standard)

LinkedIn does **not** render Markdown. All emphasis = Unicode variants via the CLI.

| Element | Treatment | Limit |
|---------|-----------|-------|
| Hook (line 1) | **Full line** Unicode bold sans | Always |
| Core thesis / gap phrase | Unicode bold | 1–2 short phrases in body |
| Key stat | Unicode bold | 0–1 |
| Closer / CTA question | **Full line** Unicode italic sans | Always |
| Emoji | 1 per section transition | 3–5 total, semantic only |
| Everything else | Plain ASCII | Default |

**Never bold >~15% of words.** Report titles with years stay plain text (cursor + search safe).

### Emoji guide (sparse, semantic)

| Section | Examples |
|---------|----------|
| Time drain / stakes | ⏳ 🕐 |
| Workflow steps | 🔄 📋 |
| Fragmentation | 🗂️ 🔍 |
| Insight / gap | 💡 |
| Closer | 💬 |

No ✨🚀🔥 on analytical posts. No emoji on the hook line.

## Writing guidelines (read before drafting)

- [linkedin-post-guideline.md](linkedin-post-guideline.md) — 8-block structure: Hook → Stakes → Evidence → Mistake → Gap → Reset → Credibility → Closer
- [Anti-AI_Writing_Guidelines.md](Anti-AI_Writing_Guidelines.md) — avoid delve/elevate, em-dash spam, rule-of-three, AI transitions

## CLI flags

```
--count --explain    Always use when delivering to user
--less-bold          Hook only
--no-hashtags        User supplies tags
--hashtags 3         Limit footer tags
--no-promote-hook    Keep original line order
```

## Limitations

Unicode bold hurts LinkedIn search and screen readers. Don't bold keywords. Not affiliated with LinkedIn or Typegrow.
